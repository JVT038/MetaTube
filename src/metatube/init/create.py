import logging
import os
import shutil
import sqlite3

from flask_migrate import init, migrate, stamp, upgrade

from metatube import Config as env
from metatube import db, logger
from metatube import migrate as metatube_migrate
from metatube.database import *
from metatube.ffmpeg import ffmpeg


class Default:
    def __init__(self, app, url):
        self._app = app
        if app.config["TESTING"] is False:
            app.app_context().push()
        self._url = url
        self._methods = ["config", "templates"]
        self._ffmpeg = app.config["FFMPEG"]
        self._downloads = app.config["DOWNLOADS"]

    def config(self):
        if Config.query.count() > 0:
            ffmpeg_instance = ffmpeg()
            ffmpeg_instance.test()
            return True
        config = Config(
            ffmpeg_directory=self._ffmpeg,
            amount=5,
            hardware_transcoding="None",
            metadata_sources="deezer",
            spotify_api="None",
            genius_api="None",
            auth=False,
            auth_username="",
            auth_password="",
        )  # type: ignore
        db.session.add(config)
        db.session.commit()
        logger.info("Created default rows for the configuration table")
        ffmpeg_instance = ffmpeg()
        ffmpeg_instance.test()
        return True

    def templates(self):
        if Templates.query.count() > 0:
            return True
        template = Templates(
            id=0,
            name="Default",
            type="Audio",
            extension="mp3",
            output_folder=self._downloads,
            output_name=f"%(title)s.%(ext)s",
            bitrate="best",
            resolution="best;best",
            default=True,
            proxy_status=False,
            proxy_username="",
            proxy_password="",
            proxy_address="",
            proxy_port="",
        )  # type: ignore
        db.session.add(template)
        db.session.commit()
        logger.info("Created default rows for the Templates table")
        return True

    def init_db(self, migrations=True):
        if migrations is False:
            directory = os.path.join(env.BASE_DIR, "migrations")
            if os.path.exists(directory):
                if len(os.listdir(directory)) > 0:
                    shutil.rmtree(directory)
            init(directory)
        self.migrations()
        for method in self._methods:
            getattr(self, method)()
        logger.info("Created the database and all necessary tables and rows")
        return True

    def migrations(self):
        directory = os.path.join(env.BASE_DIR, "migrations")
        stamp(directory)
        migrate(directory)
        if os.path.exists(self._url) and os.path.isfile(self._url):
            self.removealembic()
        upgrade(directory)

    def removealembic(self):
        conn = sqlite3.connect(self._url.replace("sqlite:///", ""))
        conn.execute("DROP TABLE IF EXISTS alembic_version;")
        conn.commit()
        conn.close()
        logger.info("Deleted alembic table")

    @metatube_migrate.configure
    def configure_alembic(config):
        logging_level_int = int(env.LOG_LEVEL)
        logging_level_name = str(logging._levelToName[logging_level_int])
        parser = config.file_config
        try:
            parser["logger_alembic"]["LEVEL"] = logging_level_name
            parser["logger_flask_migrate"]["LEVEL"] = logging_level_name
            with open(config.config_file_name, "w") as file:
                parser.write(file)
        except Exception as e:
            pass
        return config
