from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, login_user, logout_user
from models import login, UserModel
import shelve
import logging
from os import urandom

app = Flask(__name__)
# App configuration
app.config['SECRET_KEY'] = urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@scientia-db.cydo3cy4iiki.us-east-1.rds.amazonaws.com/scientiadb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Establish connection with the database.
db = SQLAlchemy(app)

# Initialise the app
db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.route('/')
def home():
    return render_template('/home.html')

@app.before_first_request
def create_all():
    db.create_all()

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
    app.run()
