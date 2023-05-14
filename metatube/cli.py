from flask import Flask
import click
from metatube import db, logger
from metatube.database import Templates, Config
from metatube.ffmpeg import ffmpeg


def register_cli(app: Flask):    
    @app.cli.command('create-config')
    def create_config():
        if Config.query.count() < 1:
            config = Config(
                ffmpeg_directory = app.config['FFMPEG'],
                amount = 5,
                hardware_transcoding = "None",
                metadata_sources='deezer',
                auth = False,
                auth_username = "",
                auth_password = ""
            )
            db.session.add(config)
            db.session.commit()
            logger.info('Created default rows for the configuration table')
        ffmpeg_instance = ffmpeg()
        ffmpeg_instance.test()
    
    @app.cli.command('create-template')
    def create_templates():
        if Templates.query.count() < 1:
            template = Templates(
                id = 0,
                name = 'Default',
                type = 'Audio',
                extension = 'mp3',
                output_folder = app.config["DOWNLOADS"],
                output_name = f"%(title)s.%(ext)s",
                bitrate = 'best',
                resolution = 'best;best',
                default = True,
                proxy_status = False,
                proxy_username = "",
                proxy_password = "",
                proxy_address = "",
                proxy_port = ""
            )
            db.session.add(template)
            db.session.commit()
            logger.info('Created default template')