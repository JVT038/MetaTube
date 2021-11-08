from flask_migrate import init, migrate, upgrade
from picardtube.database import *
from picardtube import db, migrate
from picardtube import Config as env
import os
class Default():
    def config():
        if Config.query.count() > 0:
            return True
        config = Config(
            auth = False,
            ffmpeg_directory = "",
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
            extension = 'mp3',
            output_folder = '/downloads'
        )
        db.session.add(template)
        db.session.commit()
        return True
        
    def init_db(self, db_exists = True):
        if db_exists is False:
            if os.path.isdir(os.path.join(env.BASE_DIR, 'migrations')) and os.path.exists(os.path.join(env.BASE_DIR, 'migrations')):
                upgrade(directory=os.path.join(env.BASE_DIR, 'migrations'))
            else:
                migrate(directory=os.path.join(env.BASE_DIR, 'migrations'))
                upgrade(directory=os.path.join(env.BASE_DIR, 'migrations'))
        methods = ['config', 'templates']
        for method in methods:
            getattr(Default, method)()
        return True
            
    def check_db(self):
        return True if Config.query.count() > 0 and Templates.query.count() > 0 else False