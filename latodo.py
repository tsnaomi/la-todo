import translitcodec  # necessary for Todo.slug
import re

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
    task = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))

    def __init__(self, task, list_id):
        pass

    def __unicode__(self):
        return self.item


class List(db.Model):
    ___tablename__ = 'Lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    description = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    date_updated = db.Column(db.DateTime)
    items = db.relationship('Todo', backref='list', lazy='dynamic')

    def __unicode__(self):
        return self.name

    def slug(self):  # flask.pocoo.org/snippets/5/
        punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
        result = []
        for word in punct_re.split(self.name.lower()):
            word = word.encode('translit/long')
            if word:
                result.append(word)
        return unicode(u'-'.join(result))


# Database functions ----------------------------------------------------------

def load_items():
    return Todo.query.order_by(Todo.timestamp.desc()).first()
