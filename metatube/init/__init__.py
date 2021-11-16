import os
from metatube import Config
from metatube.init.create import Default

def init(app):
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url.startswith('sqlite:///'):
        relative_url = 'sqlite:///' + os.path.join('metatube', db_url.replace('sqlite:///', ''))
        default = Default(app, relative_url)
        if os.path.exists(os.path.join(Config.BASE_DIR, 'migrations')) and os.path.isdir(os.path.join(Config.BASE_DIR, 'migrations')):
            default.init_db()
        else:
            default.init_db(db_exists = False)
    #     absolute_url = os.path.join(Config.BASE_DIR, 'metatube', db_url.replace('sqlite:///', ""))
    #     if os.path.exists(absolute_url):
    #         if default.check_db() is False:
    #             default.init_db()
    #     else:
    #         default.init_db(False)