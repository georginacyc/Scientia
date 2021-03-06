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
from urllib.request import Request, urlopen
import pymysql
import rds_db as db

from flask_login import login_required, current_user, login_user, logout_user
from models import login, UserModel
import logging
from os import urandom

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

polly = boto3.client("polly", region_name="us-east-1")

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

# Hugo's Codes
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

# Nicholas' Codes
@app.route('/donation', methods=["GET", "POST"])
def donate():
    return render_template("donation.html")

@app.route('/insert',methods = ['POST'])
def insert():
    
    if request.method == 'POST':
        tname = request.form['tname']
        amount = request.form['amount']
        db.insert_details(tname,amount)
        details = db.get_details()
        print(details)
        for detail in details:
            var = detail
        return render_template('success.html')

@app.route('/profile')
def viewProfile():
    return render_template("profile.html")

@app.route('/success')
def paymentsuccess():
    return render_template("success.html")

@app.route('/cancelled')
def paymentcancelled():
    return render_template("Oncancel.html")

# Ryan's Codes

# Initialise the app
db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!")
        return redirect('/profile')

    if request.method == 'POST':
        req_email = request.form['email']
        logging.warning(req_email)
        logging.warning(UserModel.query.filter_by(email=req_email))
        user = UserModel.query.filter_by(email=req_email).first()
        logging.warning(user)
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/profile')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in!")
        return redirect('/profile')

    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        bio = request.form['bio']
        learn = request.form['learn']
        teach = request.form['teach']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return ('Email already Present')

        user = UserModel(email=email, fname=fname, lname=lname, bio=bio, learn=learn, teach=teach)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/profile', methods=["GET", "POST"])
@login_required
def getProfile():
    return render_template('profile.html')

@app.route('/editProfile', methods=["GET", "POST"])
@login_required
def editProfile():
    if request.method == 'POST':
        email = request.form['email']

        get_user = UserModel.query.filter_by(email=email).first()
        get_user.fname = request.form['fname']
        get_user.lname = request.form['lname']
        get_user.bio = request.form['bio']
        get_user.learn = request.form['learn']
        get_user.teach = request.form['teach']

        db.session.commit()
        return redirect('/profile')

    return render_template('edit_profile.html')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)