from flask import Flask, render_template, request, redirect, url_for
from Forms import CreateUserForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import shelve, User
import pymysql
import os
import boto3

app = Flask(__name__)

# Establish connection with the database.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:scientia@database-1.cydo3cy4iiki.us-east-1.rds.amazonaws.com/scientia'
db = SQLAlchemy(app)

# Disable logs.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Migrate
migrate = Migrate(app, db)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    createUserForm = CreateUserForm(request.form)
    if request.method == 'POST' and createUserForm.validate():
        usersDict = {}
        db = shelve.open('storage.db', 'c')

        try:
            usersDict = db['Users']
        except:
            print("Error in retrieving users from database.")

        user = User.User(createUserForm.firstName.data, createUserForm.lastName.data, createUserForm.email.data,
                         createUserForm.password.data, createUserForm.bio.data, createUserForm.learn.data,
                         createUserForm.teach.data)
        usersDict[user.get_userID()] = user
        db['Users'] = usersDict

        print(user.get_firstName(), user.get_lastName(), "was stored in database with user ID = ", user.get_userID())
        db.close()
        return redirect(url_for('home'))
    return render_template('register.html', form=createUserForm)

@app.route('/retrieveUsers')
def retrieveUsers():
    usersDict = {}
    db = shelve.open('storage.db', 'r')
    usersDict = db['Users']
    db.close()

    usersList = []
    for key in usersDict:
        user = usersDict.get(key)
        usersList.append(user)

    return render_template('retrieveUsers.html', usersList=usersList, count=len(usersList))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/profile', methods=["GET", "POST"])
def getProfile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run()
