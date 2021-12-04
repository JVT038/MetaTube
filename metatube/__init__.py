from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
from flask_migrate import Migrate
from flask_socketio import SocketIO
from config import Config
import logging
db = SQLAlchemy()
migrate = Migrate()
jsglue = JSGlue()
socketio = SocketIO()

from metatube.settings import bp as bp_settings
from metatube.overview import bp as bp_overview
from metatube.init import init as init_db

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    jsglue.init_app(app)
    socketio.init_app(app, async_mode='gevent', json=json)
    app.register_blueprint(bp_overview)
    app.register_blueprint(bp_settings)
    init_db(app)
    return app

import metatube.database, metatube.routes