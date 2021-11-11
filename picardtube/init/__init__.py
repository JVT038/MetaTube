# from flask import Blueprint
# bp = Blueprint('init', __name__, static_folder='../static', template_folder='../templates/')
# from picardtube.init import routes
import os
from picardtube import Config
from picardtube.init.create import Default

def init(app):
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url.startswith('sqlite:///'):
        absolute_url = os.path.join(Config.BASE_DIR, 'picardtube', db_url.replace('sqlite:///', ""))
        relative_url = 'sqlite:///' + os.path.join('picardtube', db_url.replace('sqlite:///', ''))
        default = Default(app, relative_url)
        if os.path.exists(absolute_url):
            if default.check_db() is False:
                default.init_db()
        else:
            default.init_db(False)