from flask_migrate import init, migrate, upgrade, stamp
from metatube.database import *
from metatube import db, database
from metatube import Config as env
from sqlalchemy.engine import create_engine
from sqlalchemy import inspect
import os
class Default():
    def __init__(self, app, url):
        self._app = app
        app.app_context().push()
        self._url = url
        self._methods = ['config', 'templates']
    def config():
        if Config.query.count() > 0:
            return True
        config = Config(
            ffmpeg_directory = "",
            amount = 5,
            hardware_transcoding = "None",
            auth = False,
            auth_username = "",
            auth_password = ""
        )
        db.session.add(config)
        db.session.commit()
        print('Created default Config row')
        return True

    def templates():
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
        print('Created default Template row')
        return True
        
    def init_db(self, db_exists = True):
        if db_exists is False:
            directory = os.path.join(env.BASE_DIR, 'migrations')
            try:
                init(directory)
            except:
                pass
        self.migrations()
        for method in self._methods:
            getattr(Default, method)()
        print('Created the database and all necessary tables and rows')
        return True
    
    def migrations(self):
        directory = os.path.join(env.BASE_DIR, 'migrations')
        stamp(directory)
        migrate(directory)
        upgrade(directory)