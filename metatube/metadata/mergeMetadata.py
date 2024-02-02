from mutagen.id3._frames import (
    # Meaning of the various frames: https://mutagen.readthedocs.io/en/latest/api/id3_frames.html
    APIC, TIT2, TALB, TCON, TLAN, TRCK, TSRC, TXXX, TPE1, USLT
)
from mutagen.id3 import ID3
from mutagen.flac import FLAC, Picture
from mutagen.aac import AAC
from mutagen.wave import WAVE
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover
from metatube import sockets, logger
from config import Config
from .metadataObject import MetadataObject
from .MetadataExceptions import *
from datetime import datetime
import base64, os

class mergeMetadata():  
    
    def __init__(self, filename: str, goal: str, metadata: MetadataObject, youtube_id: str, itemId = None):
        self.filename = filename
        self.goal = goal
        self.itemId = itemId
        self.metadata = metadata
        self.youtube_id = youtube_id
        
    def mergeaudiodata(self):
        '''
        Valid fields for EasyID3:
            "album",
            "bpm",
            "compilation",
            "composer",
            "copyright",
            "encodedby",
            "lyricist",
            "length",
            "media",
            "mood",
            "title",
            "version",
            "artist",
            "albumartist",
            "conductor",
            "arranger",
            "discnumber",
            "organization",
            "tracknumber",
            "author",
            "albumartistsort",
            "albumsort",
            "composersort",
            "artistsort",
            "titlesort",
            "isrc",
            "discsubtitle",
            "language",
            "genre",
            "date",
            "originaldate",
            "performer:*",
            "musicbrainz_songid",
            "website",
            "replaygain_*_gain",
            "replaygain_*_peak",
            "musicbrainz_artistid",
            "musicbrainz_albumid",
            "musicbrainz_albumartistid",
            "musicbrainz_trmid",
            "musicip_puid",
            "musicip_fingerprint",
            "musicbrainz_albumstatus",
            "musicbrainz_albumtype",
            "releasecountry",
            "musicbrainz_discid",
            "asin",
            "performer",
            "barcode",
            "catalognumber",
            "musicbrainz_releasesongid",
            "musicbrainz_releasegroupid",
            "musicbrainz_workid",
            "acoustid_fingerprint",
            "acoustid_id"
        '''
        if self.metadata.extension == 'MP3':
            audio = EasyID3(self.filename)
            if self.metadata.source in ['spotify', 'deezer']:
                audio.RegisterTXXXKey('songid', f'{self.metadata.source.upper()}_SONGID')
                audio.RegisterTXXXKey('albumid', f'{self.metadata.source.upper()}_ALBUMID')
                audio['songid'] = self.metadata.songid
                audio['albumid'] = self.metadata.albumid
        elif self.metadata.extension == 'FLAC':
            audio = FLAC(self.filename)
        elif self.metadata.extension == 'AAC':
            audio = AAC(self.filename)
        elif self.metadata.extension == 'OPUS':
            audio = OggOpus(self.filename)
        elif self.metadata.extension == 'OGG':
            audio = OggVorbis(self.filename)
        else:
            raise InvalidAudioExtension("An invalid extension has been selected for an audio file.")

        audio["album"] = self.metadata.album
        audio["artist"] = self.metadata.artists
        audio["language"] = self.metadata.language
        audio["tracknumber"] = str(self.metadata.tracknr)
        audio["title"] = self.metadata.title
        audio["date"] = self.metadata.release_date
        audio["genre"] = self.metadata.genres
        audio['isrc'] = self.metadata.isrc
            
        if self.metadata.source == 'Musicbrainz':
            audio["musicbrainz_releasesongid"] = self.metadata.songid
            audio["musicbrainz_releasegroupid"] = self.metadata.albumid
            audio["musicbrainz_albumid"] = self.metadata.albumid
        
        audio.save()
        
        if self.metadata.lyrics != '':
            lyrics = ID3(self.filename)
            lyrics.add(USLT(encoding=3, language=self.metadata.language, desc=f'Lyrics of {self.metadata.title}', text=self.metadata.lyrics))
            lyrics.save()
        
        if self.metadata.extension == 'MP3':
            cover = ID3(self.filename)
            cover["APIC"] = APIC(
                encoding=3,
                mime=self.metadata.cover_mime_type,
                type=3,
                desc=u'Cover',
                data=self.metadata.cover
            )
            cover.save()
        else:
            cover = Picture()
            cover.data = self.metadata.cover
            cover.type = 3
            cover.mime = self.metadata.cover_mime_type
            cover.desc = 'Front cover'
            if isinstance(audio, FLAC):
                audio.add_picture(cover)
            else:
                cover_data = cover.write()
                audio["metadata_block_picture"] = [base64.b64encode(cover_data).decode('ascii')]
                audio.save()
        response =  self.metadataResponseMapper()
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
        return response
    
    def mergeid3data(self):
        if self.metadata.extension == 'WAV':
            audio = WAVE(self.filename)
        else:
            raise NoWAVExtension("The extension of the selected file was not WAV.")
        try:
            audio.add_tags()
        except Exception:
            pass
        if audio.tags is None:
            raise NoAudioTags("There are no metadata tags for this file.")
        audio.tags.add(TIT2(encoding=3, text=self.metadata.title))
        audio.tags.add(TALB(encoding=3, text=self.metadata.album))
        audio.tags.add(TCON(encoding=3, text=self.metadata.genres))
        audio.tags.add(TLAN(encoding=3, text=self.metadata.language))
        audio.tags.add(TRCK(encoding=3, text=self.metadata.tracknr))
        audio.tags.add(TSRC(encoding=3, text=self.metadata.isrc))
        audio.tags.add(TPE1(encoding=3, text=self.metadata.artists))
        if self.metadata.source == 'musicbrainz':
            audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_releasesongid', text=self.metadata.songid))
            audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_albumid', text=self.metadata.albumid))
        elif self.metadata.source == 'spotify':
            audio.tags.add(TXXX(encoding=3, desc=u'spotify_songid', text=self.metadata.songid))
            audio.tags.add(TXXX(encoding=3, desc=u'spotify_albumid', text=self.metadata.albumid))
        elif self.metadata.source == 'deezer':
            audio.tags.add(TXXX(encoding=3, desc=u'deezer_songid', text=self.metadata.songid))
            audio.tags.add(TXXX(encoding=3, desc=u'deezer_albumid', text=self.metadata.albumid))
        audio.tags.add(APIC(encoding=3, mime=self.metadata.cover_mime_type, type=3, desc=u'Cover', data=self.metadata.cover))
        
        response = self.metadataResponseMapper()
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
        return response
    
    def mergevideodata(self):
        if self.metadata.extension in ['M4A', 'MP4']:
            video = MP4(self.filename)
        else:
            raise InvalidVideoExtension("An invalid extension has been selected for a video file.")
        dateobj = datetime.strptime(self.metadata.release_date, '%Y-%m-%d') if len(self.metadata.release_date) > 0 else datetime.now().date()
        year = dateobj.year
        # iTunes metadata list / key values: https://mutagen.readthedocs.io/en/latest/api/mp4.html?highlight=M4A#mutagen.mp4.MP4Tags
        video["\xa9nam"] = self.metadata.title
        video["\xa9alb"] = self.metadata.album
        video["\xa9ART"] = self.metadata.artists
        video["\xa9gen"] = self.metadata.genres
        video["\xa9day"] = str(year)

        imageformat = MP4Cover.FORMAT_PNG if "png" in self.metadata.cover_mime_type else MP4Cover.FORMAT_JPEG
        video["covr"] = [MP4Cover(self.metadata.cover, imageformat)]
        
        video.save()
        customTags = EasyMP4(self.filename)
        response = self.metadataResponseMapper()
        
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
        return response
    
    def metadataResponseMapper(self) -> dict:
        return {
            'filepath': os.path.join(Config.BASE_DIR, self.filename),
            'name': self.metadata.title,
            'artist': self.metadata.artists,
            'album': self.metadata.album,
            'date': self.metadata.release_date,
            'image': self.metadata.cover_path,
            'songid': self.metadata.songid
        }
    
    @staticmethod
    def FLV(filename):
        pass
    
    @staticmethod
    def WEBM(filename):
        pass
    
    @staticmethod
    def MKV(filename):
        pass
    
    @staticmethod
    def AVI(filename):
        pass