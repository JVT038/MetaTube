from config import Config
from metatube.init import Default
from metatube import create_app, db
from metatube.database import Config as env
from metatube.database import Templates, Database
from datetime import datetime
import os
import unittest

basedir = os.path.abspath(os.path.dirname(__file__))

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
    
class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def testAutoCreation(self):
        db.drop_all()
        relative_url = 'sqlite:///' + os.path.join('metatube', Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', ''))
        default = Default(self.app, relative_url)
        migrationsPath = os.path.join(Config.BASE_DIR, 'migrations')
        if os.path.exists(migrationsPath) and os.path.isdir(migrationsPath) and (os.path.exists(os.path.join(migrationsPath, 'env.py')) and os.path.exists(os.path.join(migrationsPath, 'versions'))):
            default.init_db()
        else:
            default.init_db(False)
        self.assertTrue(default.init_db())
        
    def testConfigTable(self):
        config = env(
            ffmpeg_directory = self.app.config['FFMPEG'],
            amount = 5,
            hardware_transcoding = "None",
            metadata_sources='deezer',
            spotify_api = 'None',
            genius_api = 'None',
            auth = False,
            auth_username = "",
            auth_password = ""
        ) # type: ignore
        db.session.add(config)
        db.session.commit()
        
        self.assertEqual(config.get_ffmpeg(), self.app.config['FFMPEG'])
        self.assertEqual(config.get_hwt(), 'None')
        self.assertEqual(config.get_metadata_sources(), 'deezer')
        self.assertEqual(config.get_spotify(), 'None')
        self.assertEqual(config.get_genius(), 'None')
        self.assertEqual(config.get_max(), 5)
        self.assertEqual(config.query.count(), 1)
        
        config.set_amount(10)
        config.set_spotify('client; secret')
        config.set_genius('api_key')
        config.set_metadata('source')
        config.set_hwtranscoding('VAAPI')
        
        self.assertEqual(config.get_metadata_sources(), 'source')
        self.assertEqual(config.get_spotify(), 'client; secret')
        self.assertEqual(config.get_genius(), 'api_key')
        self.assertEqual(config.get_max(), 10)
        self.assertEqual(config.get_hwt(), 'VAAPI')
    
    def testTemplatesTable(self):
        defaultTemplate = Templates( # type: ignore
            id = 0,
            name = 'Default',
            type = 'Audio',
            extension = 'mp3',
            output_folder = self.app.config['DOWNLOADS'],
            output_name = f"%(title)s.%(ext)s",
            bitrate = 'best',
            resolution = 'best;best',
            default = True,
            proxy_status = False
        )
        db.session.add(defaultTemplate)
        db.session.commit()
        
        self.assertEqual(Templates.counttemplates(), 1)
        
        self.assertTrue(Templates.check_existing('Default'))
        self.assertFalse(Templates.check_existing('asdf'))
        
        self.assertIsInstance(defaultTemplate, Templates)
        self.assertEqual(defaultTemplate.id, 0)  # type: ignore
        self.assertEqual(defaultTemplate.name, 'Default')  # type: ignore
        self.assertEqual(defaultTemplate.type, 'Audio')  # type: ignore
        self.assertEqual(defaultTemplate.extension, 'mp3')  # type: ignore
        self.assertEqual(defaultTemplate.output_folder, self.app.config['DOWNLOADS'])  # type: ignore
        self.assertEqual(defaultTemplate.output_name, f"%(title)s.%(ext)s")  # type: ignore
        self.assertEqual(defaultTemplate.bitrate, 'best')  # type: ignore
        self.assertEqual(defaultTemplate.resolution, 'best;best')  # type: ignore
        self.assertEqual(defaultTemplate.default, True)  # type: ignore
        self.assertEqual(defaultTemplate.proxy_status, False)  # type: ignore
        self.assertIsNone(defaultTemplate.proxy_type)  # type: ignore
        self.assertIsNone(defaultTemplate.proxy_username)  # type: ignore
        self.assertIsNone(defaultTemplate.proxy_password)  # type: ignore
        self.assertIsNone(defaultTemplate.proxy_address)  # type: ignore
        self.assertIsNone(defaultTemplate.proxy_port)  # type: ignore
        
        newTemplateId = Templates.add({
            "name": "test",
            "type": "test",
            "ext": "mp4",
            "output_folder": self.app.config["DOWNLOADS"],
            "output_name": "%(title)s - %(artist)s.%(ext)s",
            "bitrate": "best",
            "resolution": "best;best",
            "proxy": {
                "status": True,
                "type": "socks5",
                "username": "proxy_username",
                "password": "proxy_password",
                "address": "http://localhost",
                "port": "1000"
            }
        })
        newTemplate = Templates.fetchtemplate(newTemplateId)
        newTemplate.setdefault(defaultTemplate) # type: ignore
        self.assertEqual(newTemplateId, 1)
        self.assertEqual(Templates.fetchalltemplates(), [defaultTemplate, newTemplate])
        self.assertEqual(Templates.counttemplates(), 2)
        
        newTemplate.delete() # type: ignore
        self.assertEqual(Templates.counttemplates(), 1)
        
        defaultTemplate.edit({ # type: ignore
            "name": "test",
            "type": "test",
            "ext": "mp4",
            "output_folder": "random/download/path",
            "output_name": "%(title)s - %(artist)s.%(ext)s",
            "bitrate": "worst",
            "resolution": "worst;worst",
            "proxy": {
                "status": True,
                "type": "socks5",
                "username": "proxy_username",
                "password": "proxy_password",
                "address": "http://localhost",
                "port": "1000"
            }
        })
        
        self.assertEqual(defaultTemplate.id, 0)  # type: ignore
        self.assertEqual(defaultTemplate.name, 'test')  # type: ignore
        self.assertEqual(defaultTemplate.type, 'test')  # type: ignore
        self.assertEqual(defaultTemplate.extension, 'mp4')  # type: ignore
        self.assertEqual(defaultTemplate.output_folder, 'random/download/path')  # type: ignore
        self.assertEqual(defaultTemplate.output_name, "%(title)s - %(artist)s.%(ext)s")  # type: ignore
        self.assertEqual(defaultTemplate.bitrate, 'worst')  # type: ignore
        self.assertEqual(defaultTemplate.resolution, 'worst;worst')  # type: ignore
        self.assertEqual(defaultTemplate.default, False)  # type: ignore
        self.assertEqual(defaultTemplate.proxy_status, True)  # type: ignore
        self.assertEqual(defaultTemplate.proxy_type, 'socks5')  # type: ignore
        self.assertEqual(defaultTemplate.proxy_username, 'proxy_username')  # type: ignore
        self.assertEqual(defaultTemplate.proxy_password, 'proxy_password')  # type: ignore
        self.assertEqual(defaultTemplate.proxy_address, 'http://localhost')  # type: ignore
        self.assertEqual(defaultTemplate.proxy_port, 1000)  # type: ignore
        
    def testDatabase(self):
        self.assertEqual(Database.getrecords(), [])
        
        itemId = Database.insert({
            'filepath': os.path.join(self.app.config['DOWNLOADS'], '/file.mp3'),
            'name': 'Never Gonna Give You Up',
            'artist': ['Rick Astley'],
            'album': 'Whenever You Need Somebody',
            'date': '12-11-1987',
            'image': 'https://i.scdn.co/image/ab67616d0000b273baf89eb11ec7c657805d2da0',
            'track_id': '4cOdK2wGLETKBW3PvgPWqT',
            'ytid': 'dQw4w9WgXcQ'
        })
        item = Database.fetchitem(itemId)
        
        self.assertIsInstance(item, Database)
        self.assertEqual(Database.getrecords(), [item])
        self.assertEqual(Database.searchrecords('never'), [item])
        self.assertEqual(Database.itemtodict(item), {
            'id': '1',
            'filepath': os.path.join(self.app.config['DOWNLOADS'], '/file.mp3'),
            'name': 'Never Gonna Give You Up',
            'artist': 'Rick Astley',
            'album': 'Whenever You Need Somebody',
            'date': '1987-12-11 00:00:00',
            'length': 'None',
            'cover': 'https://i.scdn.co/image/ab67616d0000b273baf89eb11ec7c657805d2da0',
            'audio_id': '4cOdK2wGLETKBW3PvgPWqT',
            'youtube_id': 'dQw4w9WgXcQ'
        })
        self.assertIs(Database.checkfile(item.filepath), item) # type: ignore
        self.assertIs(Database.checkyt(item.youtube_id), item) # type: ignore
        self.assertIs(Database.checktrackid(item.audio_id), item) # type: ignore
        
        item.update({ # type: ignore
            'filepath': os.path.join(self.app.config['DOWNLOADS'], '/test.mp3'),
            'name': 'Cool song name',
            'artist': 'Famous artist',
            'album': 'Some album',
            'date': datetime.now().date(),
            'image': '/path/to/cover.png',
            'track_id': 'someid',
            'youtube_id': 'y6120QOlsfU',
            'length': None
        })
        
        self.assertEqual(Database.itemtodict(item), {
            'id': '1',
            'filepath': os.path.join(self.app.config['DOWNLOADS'], '/test.mp3'),
            'name': 'Cool song name',
            'artist': 'Famous artist',
            'album': 'Some album',
            'date': datetime.now().strftime("%Y-%m-%d 00:00:00"),
            'length': 'None',
            'cover': '/path/to/cover.png',
            'audio_id': 'someid',
            'youtube_id': 'y6120QOlsfU'
        })
        
if __name__ == '__main__':
    unittest.main(verbosity=2)