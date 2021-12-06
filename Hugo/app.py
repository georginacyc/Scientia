from re import search
from flask import Flask, config, request, jsonify, render_template, redirect, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import boto3
from botocore.config import Config
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

app = Flask(__name__)
app.secret_key = 'dont tell anyone'

# establishing connection with RDS database. contains credentials.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientiadatabase.cuwo35oct9hp.us-east-1.rds.amazonaws.com/forumDb'
db = SQLAlchemy(app)

# basically disabling logs, so no bloating
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

client = boto3.client('translate', region_name="us-east-1")
text = "DO NOT UPGRADE TO WINDOWS 11 11 is currently extremely unstable and untested, many programs will meet with multiple issues. Please hold off the update if youre planning to do so. If you did upgrade to Windows 11, don't panic as theres an easy way to transition back into Windows 10. As long as it hasn't been more than 10 days since you installed Windows 11 theres a built in feature that allows you to revert back to Windows 10."
result = client.translate_text(Text=text, SourceLanguageCode="en",
TargetLanguageCode="es")


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
    return redirect('/forumSP');

@app.route('/search', methods=["POST"])
def searchPosts():
    # a route to handle the search data

    # retrieving search term from search bar, then redirecting back to forums page with results.
    searchForm = request.form['searchTerm']
    return redirect("/forum?s=" + str(searchForm))

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)