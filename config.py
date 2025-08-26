import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')

    # sqlite
    DATABASE = os.path.join(BASE_DIR, 'instance', 'shop.db')

    DEBUG = False
    TESTING = False