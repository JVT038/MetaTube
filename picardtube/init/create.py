from flask_migrate import init, migrate, upgrade
from picardtube.database import *
from picardtube import db, database
from picardtube import Config as env
from sqlalchemy import create_engine, inspect
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
            output_folder = 'downloads'
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
            migrate(directory)
            upgrade(directory)
        for method in self._methods:
            getattr(Default, method)()
        print('Created the database and all necessary tables and rows')
        return True
            
    def check_db(self):
        # return True if Config.query.count() > 0 and Templates.query.count() > 0 else False
        # Check if tables exist
        # engine = create_engine(self._url)
        # sqlite = sqlite3.connect(self._url.replace('sqlite:///', ''))
        # cursor = sqlite.cursor()
        # inspector = inspect(engine)
        tables = ['Config', 'Database', 'Templates']
        for table in tables:
            if ('__' + table + '__') not in dir(database) and table != 'db':
                for method in self._methods:
                    getattr(Default, method)()
                # if inspector.has_table(table):
                #     # check for columns
                #     table_instance = getattr(database, table.capitalize())
                #     columns_db = table_instance.__table__.columns.keys()
                #     columns_insp = inspector.get_columns(table)
                #     # for column in inspector.get_columns(table):
                #     for column in columns_db:
                #         if column not in columns_insp:
                #             print(column["name"])
                #             column_instance = getattr(table_instance, column)
                #             name = column_instance.name
                #             type = column_instance.type
                            
                #             query = 'ALTER TABLE ' + table + 'ADD COLUMN ' + column['name'] + str(column['type']) + 'NULL DEFAULT ' + column['default']
                #             cursor.execute(query)
                #             sqlite.commit()
                #             sqlite.close()
            else:
                print(f'Table {table} doesn\'t exist')
                db.create_all()
                print('Created all missing tables')
                for method in self._methods:
                    getattr(Default, method)()
        return True