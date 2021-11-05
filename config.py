import os
from os.path import join, dirname
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = join(dirname(__file__), '.flaskenv')
load_dotenv(dotenv_path)
class Config(object):
    ''' All environment variables are stored here ''' 
    SECRET_KEY = os.environ.get('SECRET_KEY')  or 's44wzgFU9zNCQa3z'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = os.environ.get('TEMPLATES_AUTO_RELOAD') or False
    FLASK_DEBUG= os.environ.get('FLASK_DEBUG') or False
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'production'