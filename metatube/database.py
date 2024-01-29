from metatube import db, logger, sockets
from sqlalchemy.sql import expression
from dateutil import parser

class Config(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    ffmpeg_directory = db.Column(db.String(128))
    amount = db.Column(db.Integer)
    hardware_transcoding = db.Column(db.String(16), default="None")
    metadata_sources = db.Column(db.String(128), default='deezer')
    spotify_api = db.Column(db.String(128))
    genius_api = db.Column(db.String(128))
    auth = db.Column(db.Boolean, server_default=expression.false())
    auth_username = db.Column(db.String(128))
    auth_password = db.Column(db.String(128))
    
    def ffmpeg(self, ffmpeg_path):
        self.ffmpeg_directory = ffmpeg_path
        db.session.commit()
        logger.info('Set FFmpeg path to %s', ffmpeg_path)
    
    @staticmethod
    def get_ffmpeg():
        # return db.session.get(Config, 1).ffmpeg_directory
        return db.session.get(Config, 1).ffmpeg_directory# type: ignore
    
    @staticmethod
    def get_hwt():
        return db.session.get(Config, 1).hardware_transcoding # type: ignore
    
    def set_amount(self, amount):
        self.amount = int(amount)
        db.session.commit()
        logger.info('Changed amount to %s', str(amount))

    def set_spotify(self, spotify):
        self.spotify_api = spotify
        db.session.commit()
        logger.info('Changed the Spotify API settings')
        
    def set_genius(self, genius):
        self.genius_api = genius
        db.session.commit()
        logger.info('Changed the Genius API settings')
        
    def set_metadata(self, metadata_sources):
        self.metadata_sources = metadata_sources
        db.session.commit()
        logger.info('Changed the metadata settings')
    
    def set_hwtranscoding(self, hw_transcoding):
        self.hardware_transcoding = hw_transcoding
        db.session.commit()
        logger.info('Set hardware transcoding to %s', hw_transcoding)
    
    @staticmethod
    def get_metadata_sources():
        return db.session.get(Config, 1).metadata_sources # type: ignore
    
    @staticmethod
    def get_spotify():
        return db.session.get(Config, 1).spotify_api # type: ignore
    
    @staticmethod
    def get_genius():
        return db.session.get(Config, 1).genius_api # type: ignore
    
    @staticmethod
    def get_max():
        return db.session.get(Config, 1).amount # type: ignore

class Templates(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(64), unique=True, nullable=True)
    type = db.Column(db.String(64), nullable=True)
    extension = db.Column(db.String(16), nullable=True)
    output_folder = db.Column(db.String(128), nullable=True)
    output_name = db.Column(db.String(32), nullable=True)
    bitrate = db.Column(db.String(8))
    resolution = db.Column(db.String(16))
    default = db.Column(db.Boolean, unique=False, server_default=expression.false())
    proxy_status = db.Column(db.Boolean, server_default=expression.false())
    proxy_type = db.Column(db.String(16))
    proxy_username = db.Column(db.String(128))
    proxy_password = db.Column(db.String(128))
    proxy_address = db.Column(db.String(128))
    proxy_port = db.Column(db.Integer)
    
    @staticmethod
    def check_existing(value):
        return True if Templates.query.filter_by(name = value).count() > 0 else False
    
    @staticmethod
    def counttemplates():
        return Templates.query.count()
    
    @staticmethod
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
            proxy_type = data["proxy"]["type"],
            proxy_username = data["proxy"]["username"],
            proxy_password = data["proxy"]["password"],
            proxy_address = data["proxy"]["address"],
            proxy_port = data["proxy"]["port"]
        ) # type: ignore
        db.session.add(row)
        db.session.commit()
        logger.info('Added template %s', data["name"])
        return row.id
    
    @staticmethod
    def fetchtemplate(input_id):
        return Templates.query.filter_by(id = input_id).first()
    
    @staticmethod
    def fetchalltemplates():
        return Templates.query.all()
    
    def delete(self):
        logger.info('Deleting template %s', self.name)
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def searchdefault():
        return Templates.query.filter_by(default = True).first()
        
    def setdefault(self, defaulttemplate = None):
        self.default = True
        if defaulttemplate is not None:
            defaulttemplate.default = False
        db.session.commit()
        msg = f'Set template \'{self.name}\' as default template'
        logger.info(msg)
        sockets.templatesettings({'status': 'setdefault', 'msg': msg, 'templateid': self.id})
    
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
        logger.info('Edited template %s', data["name"])
        
class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64))
    artist = db.Column(db.String(64))
    album = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    length = db.Column(db.Integer)
    cover = db.Column(db.String(256))
    audio_id = db.Column(db.String(128))
    youtube_id = db.Column(db.String(16), unique=True)
    
    @staticmethod
    def searchrecords(query):
        return Database.query.filter(Database.name.like(query + "%")).all()
    
    @staticmethod
    def itemtodict(item):
        dict = {}
        for column in item.__table__.columns:
                dict[column.name] = str(getattr(item, column.name))
        return dict
    
    @staticmethod
    def getrecords():
        return Database.query.all()
    
    @staticmethod
    def fetchitem(input_id):
        return Database.query.filter_by(id = input_id).first()
    
    @staticmethod
    def checkfile(filepath_input):
        return Database.query.filter_by(filepath = filepath_input).first()
    
    @staticmethod
    def checkyt(youtube_id_input):
        return Database.query.filter_by(youtube_id = youtube_id_input).first()
    
    @staticmethod
    def checktrackid(release_id_input):
        return Database.query.filter_by(audio_id = release_id_input).first()
    
    @staticmethod
    def insert(data):
        row = Database(
            filepath = data["filepath"],
            name = data["name"],
            artist = '; '.join(data["artist"]),
            album = data["album"],
            date = parser.parse(data["date"]),
            cover = data["image"],
            audio_id = data["track_id"],
            youtube_id = data["ytid"]
        ) # type: ignore
        db.session.add(row)
        db.session.commit()
        logger.info('Inserted item %s into database', data["name"])
        return row.id
    
    def update(self, data):
        self.filepath = data["filepath"]
        self.name = data["name"]
        self.artist = data["artist"]
        self.album = data["album"]
        self.date = data["date"]
        self.length = data["length"]
        self.cover = data["image"]
        self.audio_id = data["track_id"]
        self.youtube_id = data["youtube_id"]
        db.session.commit()
        logger.info('Updated item %s', data["name"])
        data["date"] = data["date"].strftime('%d-%m-%Y')
        sockets.overview({'msg': 'changed_metadata_db', 'data': data})
    
    def updatefilepath(self, filepath):
        self.filepath = filepath
        db.session.commit()
        logger.info('Updated filepath of item %s to %s', self.name, filepath)
        sockets.overview({'msg': 'updated_filepath', 'filepath': filepath, 'item': self.id})
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        logger.info('Deleted item %s', self.name)