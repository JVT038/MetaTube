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
    FLASK_DEBUG = False
    FLASK_ENV = 'production'
    BASE_DIR = basedir
    LOGGER = os.environ.get('LOG') or False
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 30
    SOCKET_LOG = os.environ.get('SOCKET_LOG') or False
    PORT = os.environ.get('PORT') or 5000
    FFMPEG =  os.environ.get('FFMPEG') or ""
    DOWNLOADS = os.environ.get('DOWNLOADS') or os.path.join(basedir, 'downloads')
    BUFFER_SIZE = os.environ.get('BUFFER_SIZE') or 10000000