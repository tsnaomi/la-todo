from datetime import datetime
from flask import (
    abort, Flask, redirect, render_template, request, session, url_for
    )
from flask.ext.bcrypt import Bcrypt
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.seasurf import SeaSurf
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static')
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
csrf = SeaSurf(app)
flask_bcrypt = Bcrypt(app)


# Models ----------------------------------------------------------------------

class Mage(db.Model):
    __tablename__ = 'Mages'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = flask_bcrypt.generate_password_hash(password)

    def __unicode__(self):
        return self.username


class Todo(db.Model):
    __tablename__ = 'Items'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)

    def __init__(self, item):
        self.item = item
        self.timestamp = datetime.utcnow()

    def __unicode__(self):
        return self.item


# Database functions ----------------------------------------------------------

def materialize_a_mage(username, password):
    if username and password:
        mage = Mage(username, password)
        db.session.add(mage)
        db.session.commit()
        return mage
    raise ValueError('Mage is lacking either material or originality.')


def write_item(item):
    if item and len(item) <= 120:
        todo = Todo(item)
        db.session.add(todo)
        db.session.commit()
        return todo
    raise ValueError('Task is either insufficient or overcompensating.')


def load_items():
    return Todo.query.order_by(Todo.timestamp.desc()).all()
