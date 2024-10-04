import random
import unittest
from metatube import create_app, db, socketio
from metatube.database import Templates
from metatube.youtube.youtubeUtils import utils
from metatube.youtube.download import download
from metatube.youtube.downloadExceptions import *
from metatube.youtube.manageDownloadProcess import manageDownloadProcess
from metatube.youtube.downloadOptions import downloadOptions
from metatube.metadata.metadataObject import MetadataObject
from tests.Config import TestConfig

class TestYouTube(unittest.TestCase):
    VIDEO_ID = 'dQw4w9WgXcQ'
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = socketio.test_client(self.app)
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
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def testUtils(self):
        self.assertTrue(utils.is_supported(self.VIDEO_ID))
        self.assertTrue(utils.is_supported(f"https://youtu.be/{self.VIDEO_ID}"))
        self.assertTrue(utils.is_supported(f"https://youtube.com/watch?v={self.VIDEO_ID}"))
        self.assertFalse(utils.is_supported('radioactive'))
        self.assertFalse(utils.is_supported('asdfasdf'))
        from tests.youtubeTestInfoDict import dict
        # self.assertDictEqual(utils.fetch_url(self.VIDEO_ID, False), dict) # type: ignore
        self.assertEqual(utils.verifytemplate('%(title)s.%(ext)s', dict, False), 'Rick Astley - Never Gonna Give You Up (Official Music Video).webm')
        
        utils.search('Never gonna give you up')
        templates = Templates.fetchalltemplates()
        utils.fetch_video(dict, templates, [''], templates[0])
        received = self.client.get_received()
        
    def testDownloadOptions(self):
        ytdl_options = downloadOptions(
            self.VIDEO_ID,
            'MP3',
            self.app.config['DOWNLOADS'],
            'Audio',
            '%(title)s.%(ext)s',
            '192',
            {},
            {'proxy_type': 'None'},
            self.app.config['FFMPEG'],
            "None",
            "",
            "best",
            "best",
            False,
        )
        metadata = MetadataObject(
            'Never Gonna Give You Up',
            'Rick Astley',
            'Whenever You Need Somebody',
            '',
            'Unknown',
            '1987-11-12',
            '4PTG3Z6ehGkBFwjybzWkR8',
            '6eUW0wxWtzkFdaEFsTJto6',
            1,
            random.randbytes(69),
            'https://i.scdn.co/image/ab67616d0000b27315ebbedaacef61af244262a8',
            'image/jpeg',
            'GBARL9300135',
            '',
            'MP3',
            'spotify'
        )
        from tests.expectedDownloadOptions import expectedOptions
        self.assertDictEqual(ytdl_options.downloadOptionsMapper(metadata), expectedOptions)
        
    
    def tesDownloadManager(self):
        pass
    
    def testDownloadProcess(self):
        pass