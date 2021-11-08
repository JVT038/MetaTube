# from picardtube.database import models
# from picardtube import db
# class default():
#     def createtemplate():
#         template = models.Templates()
#         template.template_id = 0
#         template.template_name = 'default'
#         template.extension = 'mp3'
#         template.output_folder = '/downloads'
#         db.session.add(template)
#         db.session.commit()
from picardtube import db

class Config(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    auth = db.Column(db.Boolean, default=False)
    ffmpeg_directory = db.Column(db.String(128))
    proxy_status = db.Column(db.Boolean, default=False)
    proxy_username = db.Column(db.String(128))
    proxy_password = db.Column(db.String(128))
    proxy_address = db.Column(db.String(128))
    proxy_port = db.Column(db.String(128))
    
    def ffmpeg(self, ffmpeg_path):
        self.ffmpeg_directory = ffmpeg_path
        print(ffmpeg_path)
        if db.session.commit():
            return True
        else:
            print(False)
            return False

class Templates(db.Model):
    template_id = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(64), unique=True)
    extension = db.Column(db.String(16))
    output_folder = db.Column(db.String(128))

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    artist = db.Column(db.String(64))
    album = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    length = db.Column(db.Integer)
    musicbrainz_id = db.Column(db.Integer, unique=True)
    youtube_id = db.Column(db.Integer, unique=True)
    authentication = db.Column(db.Boolean)
    auth_username = db.Column(db.String(128))
    auth_password = db.Column(db.String(128))

class Users():
    pass