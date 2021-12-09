import os
from os.path import join, dirname
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = join(dirname(__file__), '.flaskenv')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

class Config(object):
    ''' All environment variables are stored here ''' 
    SECRET_KEY = str(os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'metatube/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    FLASK_DEBUG= os.environ.get('DEBUG') or False
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'production'
    BASE_DIR = basedir
    PORT = os.environ.get('PORT') or 5000