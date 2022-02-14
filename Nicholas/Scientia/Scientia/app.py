from flask import Flask, config, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
import os
import boto3
from botocore.config import Config
import rds_db as db

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

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

# Nina's Codes

@app.route('/video_upload')
def upload():
    return render_template("upload_video.html")

@app.route('/video')
def display_video():
    return render_template("video.html")

#if __name__ == '__main__':
#  app.run(threaded=True, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    app.run('localhost', 4449)