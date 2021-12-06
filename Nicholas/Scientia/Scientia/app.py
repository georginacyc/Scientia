from flask import Flask, config, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import boto3
from botocore.config import Config

app = Flask(__name__)

# establishing connection with RDS database. contains credentials.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientia-db.cecynww2bmvp.us-east-1.rds.amazonaws.com/scientia_forum'
db = SQLAlchemy(app)

# basically disabling logs, so no bloating
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

class forum_posts(db.Model):
    __tablename__ = "donation"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    amount = db.Column(db.Float())
    donor = db.Column(db.String())

    def __init__(self, name, amount, donor):
        self.name = name
        self.amount = amount
        self.donor = donor
       

    # how the data is represented. this affects how the data will be returned on a query. MUST BE STRING
    # def __repr__(self):
    #     return f"{self.forum},{self.type},{self.title},{self.body},{self.author}"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/donation', methods=["GET", "POST"])
def donate():
    return render_template("donation.html")

@app.route('/profile')
def viewProfile():
    return render_template("profile.html")

@app.route('/success')
def paymentsuccess():
    return render_template("success.html")

@app.route('/cancelled')
def paymentcancelled():
    return render_template("Oncancel.html")

#if __name__ == '__main__':
 #   app.run(threaded=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)