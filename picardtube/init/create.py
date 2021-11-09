from flask_migrate import init, migrate, upgrade
from picardtube.database import *
from picardtube import db
from picardtube import Config as env
import os
class Default():
    def __init__(self, app):
        self._app = app
        app.app_context().push()
    def config():
        if Config.query.count() > 0:
            return True
        config = Config(
            auth = False,
            ffmpeg_directory = "",
            output_folder = "downloads",
            proxy_status = False,
            proxy_username = "",
            proxy_password = "",
            proxy_address = "",
            proxy_port = ""
        )
        db.session.add(config)
        db.session.commit()
        return True

    def templates():
        if Templates.query.count() > 0:
            return True
        template = Templates(
            template_id = 0,
            template_name = 'default',
            extension = 'mp3'
        )
        db.session.add(template)
        db.session.commit()
        return True
        
    def init_db(self, db_exists = True):
        if db_exists is False:
            directory = os.path.join(env.BASE_DIR, 'migrations')
            if os.path.isdir(directory) and os.path.exists(directory):
                upgrade(directory)
            else:
                init(directory)
                migrate(directory)
                upgrade(directory)
        methods = ['config', 'templates']
        for method in methods:
            getattr(Default, method)()
        return True
            
    def check_db(self):
        return True if Config.query.count() > 0 and Templates.query.count() > 0 else False