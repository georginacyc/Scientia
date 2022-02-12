from re import search
from argparse import ArgumentParser
from flask import Flask, config, request, jsonify, render_template, redirect, flash, url_for, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import sys
import boto3
from botocore.config import Config
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError


AUDIO_FORMATS = {"ogg_vorbis": "audio/ogg",
                 "mp3": "audio/mpeg",
                 "pcm": "audio/wave; codecs=1"}

app = Flask(__name__)
app.secret_key = os.urandom(24)

# establishing connection with RDS database. contains credentials.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientia-db.cecynww2bmvp.us-east-1.rds.amazonaws.com/scientia_forum'
db = SQLAlchemy(app)

# basically disabling logs, so no bloating
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

polly = boto3.client("polly")

# simple function that calles teh aws function and translates any inputted text.
client = boto3.client('translate', region_name="us-east-1")
text = "DO NOT UPGRADE TO WINDOWS 11 11 is currently extremely unstable and untested, many programs will meet with multiple issues. Please hold off the update if youre planning to do so. If you did upgrade to Windows 11, don't panic as theres an easy way to transition back into Windows 10. As long as it hasn't been more than 10 days since you installed Windows 11 theres a built in feature that allows you to revert back to Windows 10."
result = client.translate_text(Text=text, SourceLanguageCode="en",
TargetLanguageCode="de")


# Simple exception class
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
        
# Register error handler
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
    
@app.route('/read', methods=['GET'])
def read():
    """Handles routing for reading text (speech synthesis)"""
    # Get the parameters from the query string
    try:
        outputFormat = request.args.get('outputFormat')
        text = request.args.get('text')
        voiceId = request.args.get('voiceId')
    except TypeError:
        raise InvalidUsage("Wrong parameters", status_code=400)

    # Validate the parameters, set error flag in case of unexpected
    # values
    if len(text) == 0 or len(voiceId) == 0 or \
            outputFormat not in AUDIO_FORMATS:
        raise InvalidUsage("Wrong parameters", status_code=400)
    else:
        try:
            # Request speech synthesis
            response = polly.synthesize_speech(Text=text,
                                               VoiceId=voiceId,
                                               OutputFormat=outputFormat)
        except (BotoCoreError, ClientError) as err:
            # The service returned an error
            raise InvalidUsage(str(err), status_code=500)

        return send_file(response.get("AudioStream"),
                         AUDIO_FORMATS[outputFormat])

@app.route('/voices', methods=['GET'])
def voices():
    """Handles routing for listing available voices"""
    params = {}
    voices = []

    try:
        # Request list of available voices, if a continuation token
        # was returned by the previous call then use it to continue
        # listing
        response = polly.describe_voices(**params)
    except (BotoCoreError, ClientError) as err:
        # The service returned an error
        raise InvalidUsage(str(err), status_code=500)

    # Collect all the voices
    voices.extend(response.get("Voices", []))

    return jsonify(voices)


# Define and parse the command line arguments
cli = ArgumentParser(description='Example Flask Application')
cli.add_argument(
    "-p", "--port", type=int, metavar="PORT", dest="port", default=8000)
cli.add_argument(
    "--host", type=str, metavar="HOST", dest="host", default="localhost")
arguments = cli.parse_args()

class forum_posts(db.Model):
    __tablename__ = "forum_posts"

    id = db.Column(db.Integer, primary_key=True)
    forum = db.Column(db.String())
    type = db.Column(db.String())
    title = db.Column(db.String())
    body = db.Column(db.String())
    author = db.Column(db.String())

    def __init__(self, forum: str, type: str, title: str, body: str, author: str):
        self.forum = forum
        self.type = type
        self.title = title
        self.body = body
        self.author = author

    # how the data is represented. this affects how the data will be returned on a query. MUST BE STRING
    # def __repr__(self):
    #     return f"{self.forum},{self.type},{self.title},{self.body},{self.author}"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/forum', methods=["GET", "POST"])
def getPosts():
    # retrieving a search term, if any
    search_term = request.args.get('s', default=None, type=str)
    search_term = "%{}%".format(search_term)

    # checks if there is a search term
    if search_term != "%None%":
        # chain queries together so that search terms dont just search the "body" of a post
        query = forum_posts.query.filter((forum_posts.body.like(search_term)) | (forum_posts.title.like(search_term)) | (forum_posts.body.like(search_term)))
        posts = query.all()
    else:
        posts = forum_posts.query.all()
    
    return render_template("forum_posts.html", posts=posts)

@app.route('/forumSP', methods=["GET", "POST"])
def getPostsSP():
    return render_template("forum_posts_trans.html")

@app.route('/forumTR', methods=["POST"])
def transButton():
    flash (result['TranslatedText'])
    return redirect('/forumSP')

@app.route('/search', methods=["POST"])
def searchPosts():
    # a route to handle the search data

    # retrieving search term from search bar, then redirecting back to forums page with results.
    searchForm = request.form['searchTerm']
    return redirect("/forum?s=" + str(searchForm))

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)