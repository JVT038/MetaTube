from flask_migrate import init, migrate, upgrade, stamp
from metatube.database import *
from metatube import db, logger
from metatube import Config as env
from sqlalchemy.engine import create_engine
from sqlalchemy import inspect
import sqlite3
import os
class Default():
    def __init__(self, app, url, ffmpeg):
        self._app = app
        app.app_context().push()
        self._url = url
        self._methods = ['config', 'templates']
        self._ffmpeg = ffmpeg
    def config(self):
        if Config.query.count() > 0:
            return True
        config = Config(
            ffmpeg_directory = self._ffmpeg,
            amount = 5,
            hardware_transcoding = "None",
            auth = False,
            auth_username = "",
            auth_password = ""
        )
        db.session.add(config)
        db.session.commit()
        logger.info('Created default rows for the configuration table')
        return True

    def templates(self):
        if Templates.query.count() > 0:
            return True
        template = Templates(
            id = 0,
            name = 'Default',
            type = 'Audio',
            extension = 'mp3',
            output_folder = 'downloads',
            output_name = f"%(title)s.%(ext)s",
            bitrate = 192,
            resolution = 'None',
            proxy_status = False,
            proxy_username = "",
            proxy_password = "",
            proxy_address = "",
            proxy_port = ""
        )
        db.session.add(template)
        db.session.commit()
        logger.info('Created default rows for the Templates table')
        return True
        
    def init_db(self, db_exists = True):
        if db_exists is False:
            directory = os.path.join(env.BASE_DIR, 'migrations')
            if os.path.exists(directory):
                init(directory)    
                self.removealembic()
        self.migrations()
        for method in self._methods:
            getattr(self, method)()
        logger.info('Created the database and all necessary tables and rows')
        return True
    
    def migrations(self):
        directory = os.path.join(env.BASE_DIR, 'migrations')
        stamp(directory)
        migrate(directory)
        upgrade(directory)
        
    def removealembic(self):
        conn = sqlite3.connect(self._url.replace('sqlite:///', ''))
        conn.execute('DROP TABLE IF EXISTS alembic_version;')
        conn.commit()
        conn.close()
        logger.info('Deleted alembic table')