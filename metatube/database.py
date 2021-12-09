from metatube import db
from dateutil import parser

class Config(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    auth = db.Column(db.Boolean, default=False)
    ffmpeg_directory = db.Column(db.String(128))
    amount = db.Column(db.Integer)
    hardware_transcoding = db.Column(db.String(16), default="None")
    auth = db.Column(db.Boolean)
    auth_username = db.Column(db.String(128))
    auth_password = db.Column(db.String(128))
    
    def ffmpeg(self, ffmpeg_path):
        self.ffmpeg_directory = ffmpeg_path
        db.session.commit()
    
    def get_ffmpeg():
        return Config.query.get(1).ffmpeg_directory
    
    def get_hwt():
        return Config.query.get(1).hardware_transcoding
    
    def set_amount(self, amount):
        self.amount = int(amount)
        db.session.commit()
    
    def set_hwtranscoding(self, hw_transcoding):
        self.hardware_transcoding = hw_transcoding
        db.session.commit()
    
    def get_max():
        return Config.query.get(1).amount

class Templates(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(64), unique=True, nullable=True)
    type = db.Column(db.String(64), nullable=True)
    extension = db.Column(db.String(16), nullable=True)
    output_folder = db.Column(db.String(128), nullable=True)
    output_name = db.Column(db.String(32), nullable=True)
    bitrate = db.Column(db.Integer)
    resolution = db.Column(db.String(16))
    proxy_status = db.Column(db.Boolean, default=False)
    proxy_type = db.Column(db.String(16))
    proxy_username = db.Column(db.String(128))
    proxy_password = db.Column(db.String(128))
    proxy_address = db.Column(db.String(128))
    proxy_port = db.Column(db.Integer)
    
    def check_existing(value):
        return True if Templates.query.filter_by(name = value).count() > 0 else False
    
    def add(data):
        row = Templates(
            name = data["name"],
            type = data["type"],
            extension = data["ext"],
            output_folder = data["output_folder"],
            output_name = data["output_name"],
            bitrate = data["bitrate"],
            resolution = data["resolution"],
            proxy_status = data["proxy"]["status"],
            proxy_username = data["proxy"]["username"],
            proxy_password = data["proxy"]["password"],
            proxy_address = data["proxy"]["address"],
            proxy_port = data["proxy"]["port"]
        )
        db.session.add(row)
        db.session.commit()
    
    def fetchtemplate(input_id):
        return Templates.query.filter_by(id = input_id).first()
    
    def fetchalltemplates():
        return Templates.query.all()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def edit(self, data):
        self.name = data["name"]
        self.type = data["type"]
        self.extension = data["ext"]
        self.output_folder = data["output_folder"]
        self.output_name = data["output_name"]
        self.bitrate = data["bitrate"]
        self.resolution = data["resolution"]
        self.proxy_status = data["proxy"]["status"]
        self.proxy_type = data["proxy"]['type']
        self.proxy_username = data["proxy"]["username"]
        self.proxy_password = data["proxy"]["password"]
        self.proxy_address = data["proxy"]["address"]
        self.proxy_port = data["proxy"]["port"]
        db.session.commit()
        
class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    artist = db.Column(db.String(64))
    album = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    length = db.Column(db.Integer)
    cover = db.Column(db.LargeBinary)
    musicbrainz_id = db.Column(db.String(128), unique=True)
    youtube_id = db.Column(db.String(16), unique=True)
    
    def getrecords():
        return Database.query.all()
    
    def fetchitem(input_id):
        return Database.query.filter_by(id = input_id).first()
    
    def checkfile(filepath_input):
        return Database.query.filter_by(filepath = filepath_input).first()
    
    def checkyt(youtube_id_input):
        return Database.query.filter_by(youtube_id = youtube_id_input).first()
    
    def insert(data):
        row = Database(
            filepath = data["filepath"],
            name = data["name"],
            artist = data["artist"],
            album = data["album"],
            date = parser.parse(data["date"]),
            cover = data["image"],
            musicbrainz_id = data["musicbrainz_id"],
            youtube_id = data["ytid"]
        )
        db.session.add(row)
        db.session.commit()
        return row.id
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()