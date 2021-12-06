from re import search
from flask import Flask, config, request, jsonify, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import boto3
from botocore.config import Config
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

app = Flask(__name__)

# establishing connection with RDS database. contains credentials.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientiadatabase.cuwo35oct9hp.us-east-1.rds.amazonaws.com/forumDb'
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

client = boto3.client('translate', region_name="us-east-1")
text = "DO NOT UPGRADE TO WINDOWS 11 <br> 11 is currently extremely unstable and untested, many programs will meet with multiple issues. <br> Please hold off the update if youre planning to do so. <br> If you did upgrade to Windows 11, don't panic as theres an easy way to transition back into Windows 10. <br> As long as it hasn't been more than 10 days since you installed Windows 11 theres a built in feature that allows you to revert back to Windows 10.<br><br>"
result = client.translate_text(Text=text, SourceLanguageCode="en",
    TargetLanguageCode="es")
print(result['TranslatedText'])