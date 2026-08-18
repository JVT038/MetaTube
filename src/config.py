import os
from os.path import dirname, join

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = join(dirname(__file__), ".flaskenv")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config(object):
    """All environment variables are stored here"""

    SECRET_KEY = str(os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "metatube/app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    FLASK_DEBUG = False
    FLASK_ENV = "production"
    BASE_DIR = basedir
    LOGGER = os.environ.get("LOG", False)
    LOG_LEVEL = os.environ.get("LOG_LEVEL", 10)
    SOCKET_LOG = os.environ.get("SOCKET_LOG", False)
    PORT = os.environ.get("PORT", 5000)
    FFMPEG = os.environ.get("FFMPEG", "")
    DOWNLOADS = os.environ.get("DOWNLOADS", os.path.join(basedir, "downloads"))
    URL_SUBPATH = os.environ.get("URL_SUBPATH", "/")
    META_EXTENSIONS = ["MP3", "OPUS", "FLAC", "OGG", "MP4", "M4A", "WAV"]
    VIDEO_EXTENSIONS = ["MP4", "M4A", "FLV", "WEBM", "OGG", "MKV", "AVI"]
    AUDIO_EXTENSIONS = ["AAC", "FLAC", "MP3", "M4A", "OPUS", "VORBIS", "WAV"]
    INIT_DB = os.environ.get("INIT_DB", True)
    TESTING = False
