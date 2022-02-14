from flask import Flask, render_template, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from os import urandom

login = LoginManager()
db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    bio = db.Column(db.String())
    learn = db.Column(db.String())
    teach = db.Column(db.String())
    tips = db.Column(db.Integer)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class TransactionModel(db.Model):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.String, primary_key=True)
    tipper_name = db.Column(db.String(100))
    tip_to_email = db.Column(db.String(100))
    amount = db.Column(db.Integer)