from datetime import timedelta
from random import choice
from string import printable


def secret_key():
    secret_key = ''
    for num in range(40):
        secret_key += choice(printable)
    return secret_key

PERMANENT_SESSION_LIFETIME = timedelta(weeks=1)
SECRET_KEY = secret_key()
SQLALCHEMY_DATABASE_URI = 'postgresql:///latodoliste'
TESTING = True
