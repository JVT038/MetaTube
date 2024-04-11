from mutagen.flac import FLAC
from mutagen.aac import AAC
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from magic import Magic
from metatube import logger
from config import Config as env
from .MetadataExceptions import *
from .metadataObject import MetadataObject
import requests

class readMetadata(object):
    @staticmethod
    def getImage(cover_path) -> dict:
        magic = Magic(mime=True)
        if cover_path != env.DEFAULT_COVER_PATH and cover_path != '':
            try:
                response = requests.get(cover_path)
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
                return {
                    'mime_type' : cover_mime_type,
                    'image': image
                }
            except Exception:               
                raise InvalidCoverURL("Cover URL is invalid!")
        else:
            file = open(env.DEFAULT_COVER_PATH, 'rb')
            return {
                    'mime_type' : 'image/png',
                    'image': file.read()
            }
    
    @staticmethod
    def readAudioMetadata(filename, songid, cover_path) -> MetadataObject:
        logger.info('Reading metadata of %s', filename)
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension == 'MP3':
            audio = EasyID3(filename)
        elif extension == 'FLAC':
            audio = FLAC(filename)
        elif extension == 'AAC':
            audio = AAC(filename)
        elif extension == 'OPUS':
            audio = OggOpus(filename)
        elif extension == 'OGG':
            audio = OggVorbis(filename)
        else:
            raise InvalidAudioFile("The selected audio file has an invalid extension.")
        
        coverdata = readMetadata.getImage(cover_path)
        source = ''
        songid = ''
        albumid = ''
        
        if 'SPOTIFY_SONGID' in audio:
            source = 'spotify'
        elif 'DEEZER_SONGID' in audio:
            source = 'deezer'
        elif 'musicbrainz_releasesongid' in audio:
            source = 'musicbrainz'
            
        if songid == '':
            songid = audio.get('SPOTIFY_SONGID', [''])[0] # type: ignore
        if songid == '':
            songid = audio.get('DEEZER_SONGID', [''])[0] # type: ignore
        if songid == '':
            songid = audio.get('musicbrainz_releasesongid', [''])[0] # type: ignore
            
        if albumid == '':
            albumid = audio.get('SPOTIFY_ALBUMID', [''])[0] # type: ignore
        if albumid == '':
            albumid = audio.get('DEEZER_ALBUMID', [''])[0] # type: ignore
        if albumid == '':
            albumid = audio.get('musicbrainz_releasealbumid', [''])[0] # type: ignore
        
        return MetadataObject(
            audio.get('title', [''])[0], # type: ignore
            audio.get('artist', [''])[0], # type: ignore
            audio.get('album', [''])[0], # type: ignore
            audio.get('genre', [''])[0], # type: ignore
            audio.get('language', [''])[0], # type: ignore
            audio.get('date', [''])[0], # type: ignore
            songid,
            albumid,
            audio.get('tracknumber', [''])[0], # type: ignore
            coverdata['image'],
            cover_path,
            coverdata['mime_type'],
            audio.get('isrc', [''])[0], # type: ignore
            audio.get('lyrics', [''])[0], # type: ignore
            extension,
            source
        )
    
    @staticmethod
    def readVideoMetadata(filename, songid, cover_path) -> MetadataObject:
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension in ['M4A', 'MP4']:
            video = MP4(filename)
        else:
            raise InvalidAudioFile("The selected video file has an invalid extension")
        
        coverdata = readMetadata.getImage(cover_path)
                
        return MetadataObject(
            video.get('\xa9nam', [''])[0], # type: ignore
            video.get("\xa9ART", [''])[0], # type: ignore
            video.get("\xa9alb", [''])[0], # type: ignore
            video.get("\xa9gen", [''])[0], # type: ignore
            "Unknown",
            video.get("\xa9day", [''])[0], # type: ignore
            songid,
            '',
            1,
            coverdata['image'],
            cover_path,
            coverdata['mime_type'],
            "Unknown",
            "",
            extension,
            ''
        )