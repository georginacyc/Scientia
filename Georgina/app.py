from re import search
from flask import Flask, config, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import boto3
from botocore.config import Config

app = Flask(__name__)

# establishing connection with RDS database. contains credentials.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientia.cecynww2bmvp.us-east-1.rds.amazonaws.com/scientiaTest'
db = SQLAlchemy(app)

# basically disabling logs, so no bloating
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

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

@app.route('/search', methods=["POST"])
def searchPosts():
    # a route to handle the search data

    # retrieving search term from search bar, then redirecting back to forums page with results.
    searchForm = request.form['searchTerm']
    return redirect("/forum?s=" + str(searchForm))

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)