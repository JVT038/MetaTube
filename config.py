import os
from os.path import join, dirname
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = join(dirname(__file__), '.flaskenv')
os.environ.setdefault('WERKZEUG_RUN_MAIN', 'true')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    os.environ.setdefault('FLASK_APP', 'picardtube.py')
class Config(object):
    ''' All environment variables are stored here ''' 
    SECRET_KEY = os.environ.get('SECRET_KEY')  or 's44wzgFU9zNCQa3z'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = os.environ.get('TEMPLATES_AUTO_RELOAD') or False
    FLASK_DEBUG= os.environ.get('FLASK_DEBUG') or False
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'production'
    BASE_DIR = basedir
    PORT = os.environ.get('PORT') or 5000