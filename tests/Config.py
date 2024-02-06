from metatube import Config
class TestConfig(Config):
    TESTING = True
    FFMPEG = 'bin'
    META_EXTENSIONS = ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV']
    VIDEO_EXTENSIONS = ['MP4', 'M4A', 'FLV', 'WEBM', 'OGG', 'MKV', 'AVI']
    AUDIO_EXTENSIONS = ['AAC', 'FLAC', 'MP3', 'M4A', 'OPUS', 'VORBIS', 'WAV']
    DOWNLOADS = '/path/to/downloads'
    LOGGER = False
    LOG_LEVEL = 40
    INIT_DB = False
    # SQLALCHEMY_DATABASE_URI = os.path.join('sqlite:///', basedir, 'metatube/test.db')
    # SQLALCHEMY_DATABASE_URI = 'sqlite://'