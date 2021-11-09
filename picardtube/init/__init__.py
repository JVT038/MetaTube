# from flask import Blueprint
# bp = Blueprint('init', __name__, static_folder='../static', template_folder='../templates/')
# from picardtube.init import routes
import os
from picardtube import Config
from picardtube.init.create import Default

def init(app):
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url.startswith('sqlite:///'):
        default = Default(app)
        if os.path.exists(os.path.join(Config.BASE_DIR, 'picardtube', db_url.replace('sqlite:///', ""))):
            if default.check_db():
                print('DB is ok')
            else:
                print('DB doesn\'t have default rows')
                default.init_db()
                print('DB rows created')
        else:
            print('DB doesn\'t exist')
            default.init_db(False)
            print('DB + rows created')