from datetime import datetime
from flask import (flash, Flask, redirect, render_template, request, session,
                   url_for)
from flask.ext.bcrypt import Bcrypt
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.seasurf import SeaSurf
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.exc import IntegrityError


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
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = flask_bcrypt.generate_password_hash(password)

    def __unicode__(self):
        return self.username


class Todo(db.Model):
    __tablename__ = 'Items'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime)

    def __init__(self, item):
        self.item = item
        self.timestamp = datetime.utcnow()

    def __unicode__(self):
        return self.item


# Database functions ----------------------------------------------------------

def materialize_a_mage(username, password):
    if username and password:
        try:
            mage = Mage(username, password)
            db.session.add(mage)
            db.session.commit()
            return mage
        except IntegrityError:
            raise ValueError('Mage is lacking originality')
    else:
        raise ValueError('Mage is lacking material.')


def write_item(item):
    if item and len(item) <= 120:
        todo = Todo(item)
        db.session.add(todo)
        db.session.commit()
        return todo
    raise ValueError('Item is either insufficient or overcompensating.')


def delete_item(id):
    if Todo.query.get(id):
        db.session.delete(Todo.query.get(id))
        db.session.commit()
    else:
        raise KeyError('Item does not exist.')


def load_items():
    return Todo.query.order_by(Todo.timestamp.desc()).all()


# Views -----------------------------------------------------------------------

@app.before_request
def renew_session():
    session.modified = True


def login_required(x):
    @wraps(x)
    def decorator(*args, **kwargs):
        if session.get('current_user'):
            return x(*args, **kwargs)
        return redirect(url_for('login_view'))
    return decorator


@app.route('/', methods=['GET', 'POST'])
@login_required
def list_view():
    if request.method == 'POST':
        try:
            write_item(request.form['todo'])
            return redirect(url_for('list_view'))
        except ValueError as E:
            print E
    return render_template('list.html', items=load_items())


@app.route('/expel/<id>', methods=['GET', ])
@login_required
def delete_view(id):
    try:
        delete_item(id)
    except KeyError as E:
        print E
    return redirect(url_for('list_view'))


@app.route('/join', methods=['GET', 'POST'])
def registration_view():
    if request.method == 'POST':
        try:
            materialize_a_mage(request.form['username'],
                               request.form['password'])
            return redirect(url_for('login_view'))
        except ValueError:
            flash('Unsuccessful.')
    return render_template('register.html')


@app.route('/enter', methods=['GET', 'POST'])
def login_view():
    if session.get('current_user'):
        return redirect(url_for('list_view'))
    if request.method == 'POST':
        mage = Mage.query.filter_by(username=request.form['username']).first()
        password = request.form['password']
        if mage is None or not flask_bcrypt.check_password_hash(mage.password,
                                                                password):
            flash('Invalid.')
        else:
            session['current_user'] = mage.username
            return redirect(url_for('list_view'))
    return render_template('login.html')


@app.route('/leave')
def logout_view():
    session.pop('current_user', None)
    return redirect(url_for('login_view'))


# Error handling --------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='404: Page Not Found')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message='500: Internal Server Error')


if __name__ == '__main__':
    manager.run()
