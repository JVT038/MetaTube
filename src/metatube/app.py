from gevent import monkey

monkey.patch_all()
import logging

from flask import Flask, json
from flask.logging import default_handler
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from config import Config
from metatube.utils import strtobool

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

logformat = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
    datefmt="%d-%m-%Y %H:%M",
)

console = logging.StreamHandler()
console.setFormatter(fmt=logformat)

logger = logging.getLogger("default")
logger.addHandler(console)

from metatube.init import init as init_db
from metatube.overview import bp as bp_overview
from metatube.routes import error
from metatube.settings import bp as bp_settings


def create_app(config_class=Config):
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object(config_class)
    app.config.update(FLASK_DEBUG=False, FLASK_ENV="production")
    app.register_error_handler(Exception, error)
    app.logger.removeHandler(default_handler)
    app.logger.addHandler(console)
    console.setLevel(int(app.config["LOG_LEVEL"]))
    socket_log = logger if strtobool(str(app.config["SOCKET_LOG"])) == 1 else False
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True, ping_interval=60)
    socketio.init_app(
        app,
        json=json,
        engineio_logger=socket_log,
        logger=socket_log,
        async_mode="gevent",
    )
    app.register_blueprint(bp_overview)
    app.register_blueprint(bp_settings)
    if app.config.get("INIT_DB") == True:
        init_db(app)
    return app

import metatube.database