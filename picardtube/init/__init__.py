# from flask import Blueprint
# bp = Blueprint('init', __name__, static_folder='../static', template_folder='../templates/')
# from picardtube.init import routes
import os
from flask import url_for, redirect, render_template
from picardtube import Config
from picardtube.database.start import Default
from functools import wraps
    
def checkdb(f):
    @wraps(f)
    def init(*args, **kwargs):
        db_url = Config.SQLALCHEMY_DATABASE_URI
        if db_url.startswith('sqlite:///'):
            default = Default()
            if os.path.exists(os.path.join(Config.BASE_DIR, 'picardtube', db_url.replace('sqlite:///', ""))):
                if default.check_db():
                    print('DB is ok')
                    return f(*args, **kwargs)
                else:
                    print('DB doesn\'t have default rows')
                    default.init_db()
                    return f(*args, **kwargs)
            else:
                print('DB doesn\'t exist')
                default.init_db(False)
                return f(*args, **kwargs)
                
        elif db_url.startswith('mysql'):
            return f(*args, **kwargs)
    return init