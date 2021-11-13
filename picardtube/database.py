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
        db.session.commit()
        return True
    
    def get_ffmpeg():
        return Config.query.get(1).ffmpeg_directory

class Templates(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(64), unique=True, nullable=True)
    type = db.Column(db.String(64), nullable=True)
    extension = db.Column(db.String(16), nullable=True)
    output_folder = db.Column(db.String(128), nullable=True)
    output_name = db.Column(db.String(32), nullable=True)
    bitrate = db.Column(db.Integer)
    
    def check_existing(value):
        return True if Templates.query.filter_by(name = value).count() > 0 else False
    
    def add(data):
        row = Templates(
            name = data.name,
            type = data.type,
            extension = data.ext,
            output_folder = data.output_folder,
            output_name = data.output_name,
            bitrate = data.bitrate
        )
        db.session.add(row)
        db.session.commit()
        return True
    
    def fetchtemplate(input_id):
        return Templates.query.filter_by(id = input_id).first()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return True
    
    def edit(self, data):
        self.name = data.name
        self.type = data.type
        self.extension = data.ext
        self.output_folder = data.output_folder
        self.output_name = data.output_name
        self.bitrate = data.bitrate
        db.session.commit()
        return True

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))