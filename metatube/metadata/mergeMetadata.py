from mutagen.id3._frames import (
    # Meaning of the various frames: https://mutagen.readthedocs.io/en/latest/api/id3_frames.html
    APIC, TIT2, TALB, TCON, TLAN, TRCK, TSRC, TXXX, TPE1
)
from mutagen.id3 import ID3
from mutagen.flac import FLAC, Picture
from mutagen.aac import AAC
from mutagen.wave import WAVE
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
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
    
    def __init__(self, filename: str, goal: str, metadata: MetadataObject, itemId = None):
        self.filename = filename
        self.goal = goal
        self.itemId = itemId
        self.metadata = metadata
        
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
            if self.metadata.source == 'Spotify':
                audio.RegisterTXXXKey('spotify_songid', self.metadata.songid)
                audio.RegisterTXXXKey('spotify_albumid', self.metadata.albumid)
            elif self.metadata.source == 'Deezer':
                audio.RegisterTXXXKey('deezer_songid', self.metadata.songid)
                audio.RegisterTXXXKey('deezer_albumid', self.metadata.albumid)
            if self.metadata.lyrics is not None:
                audio.RegisterTextKey('lyrics', "USLT")            
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
        if self.metadata.lyrics is not None and self.metadata.extension != 'MP3':
            audio['lyrics'] = self.metadata.lyrics
        if self.metadata.source == 'Musicbrainz':
            audio["musicbrainz_releasesongid"] = self.metadata.songid
            audio["musicbrainz_releasegroupid"] = self.metadata.albumid
            audio["musicbrainz_albumid"] = self.metadata.albumid
        
        audio.save()
        
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
        response =  self.metadataResponseMapper(self.metadata.length)
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
            sockets.finished_metadata(response)
    
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
        audio.tags.add(TALB(encoding=3, text=self.metadata.album)) # type: ignore
        audio.tags.add(TCON(encoding=3, text=self.metadata.genres)) # type: ignore
        audio.tags.add(TLAN(encoding=3, text=self.metadata.language)) # type: ignore
        audio.tags.add(TRCK(encoding=3, text=self.metadata.tracknr)) # type: ignore
        audio.tags.add(TSRC(encoding=3, text=data["isrc"])) # type: ignore
        audio.tags.add(TPE1(encoding=3, text=self.metadata.artists)) # type: ignore
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_releasesongid', text=data["mbp_songid"])) # type: ignore
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_releasegroupid', text=data['mbp_albumid'])) # type: ignore
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_albumid', text=data["mbp_albumid"])) # type: ignore
        audio.tags.add(APIC(encoding=3, mime=self.metadata.cover_mime_type, type=3, desc=u'Cover', data=self.metadata.cover)) # type: ignore
        
        response = self.metadataResponseMapper(self.metadata.length)
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
            sockets.finished_metadata(response)
    
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
        try:
            video["trkn"] = [(int(self.metadata.tracknr), int(self.metadata.total_tracks))]
        except Exception:
            pass
        imageformat = MP4Cover.FORMAT_PNG if "png" in self.metadata.cover_mime_type else MP4Cover.FORMAT_JPEG
        video["covr"] = [MP4Cover(self.metadata.cover, imageformat)]
        
        video.save()
        response = self.metadataResponseMapper(self.metadata.length)
        
        if self.goal == 'edit':
            response["itemid"] = self.itemId
            logger.info('Finished changing metadata of %s', self.metadata.title)
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif self.goal == 'add':
            logger.info('Finished adding metadata to %s', self.metadata.title)
            sockets.finished_metadata(response)
    
    @staticmethod
    def readaudiometadata(filename):
        logger.info('Reading metadata of %s', filename)
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension == 'MP3':
            audio = EasyID3(filename)
            data = MP3(filename)
        elif extension == 'FLAC':
            audio = FLAC(filename)
            data = FLAC(filename)
        elif extension == 'AAC':
            audio = AAC(filename)
            data = FLAC(filename)
        elif extension == 'OPUS':
            audio = OggOpus(filename)
            data = OggOpus(filename)
        elif extension == 'OGG':
            audio = OggVorbis(filename)
            data = OggVorbis(filename)
        else:
            raise InvalidAudioFile("The selected audio file has an invalid extension.")
        
        response = {
            'title': (audio['title'] or [''])[0],
            'artists': (audio['artist'] or [''])[0],
            'album': (audio['album'] or [''])[0],
            'barcode': (audio['barcode'] or [''])[0],
            'genres': (audio['genre'] or [''])[0],
            'language': (audio['language'] or [''])[0],
            'release_date': (audio['date'] or [''])[0],
            'album_id': "",
            'total_tracks': "",
            'mbp_songid': (audio['musicbrainz_releasesongid'] or [''])[0],
            'mbp_releasegroupid': (audio['musicbrainz_releasegroupid'] or [''])[0],
            'isrc': (audio['isrc'] or [''])[0],
            'tracknr': (audio['tracknumber'] or [''])[0],
            'date': (audio['date'] or [''])[0],
            'length': data.info.length, # type: ignore
            'bitrate': data.info.bitrate, # type: ignore
            'output_folder': os.path.dirname(filename),
            'filename': filename,
            "goal": "edit",
        }
        
        return response
    
    @staticmethod
    def readvideometadata(filename) -> dict | None:
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension in ['M4A', 'MP4']:
            video = MP4(filename)
        else:
            raise InvalidAudioFile("The selected video file has an invalid extension")
            
        # Bitrate calculation: https://www.reddit.com/r/headphones/comments/3xju4s/comment/cy5dn8h/?utm_source=share&utm_medium=web2x&context=3
        # Mutagen MP4 stream info: https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Info
        bitrate = int(video.info.bits_per_sample * video.info.sample_rate * video.info.channels)
        response = {
            'title': (video['\xa9nam'] or [''])[0],
            'album': (video["\xa9alb"] or [''])[0],
            'artists': (video["\xa9ART"] or [''])[0],
            'genres': (video["\xa9gen"] or [''])[0],
            'release_date': (video["\xa9day"] or [''])[0],
            'bitrate': bitrate,
            'output_folder': os.path.dirname(filename),
            'filename': filename,
            'length': video.info.length,
            'tracknr': video.get('trkn', [[1]])[0][0] # type: ignore
        }
        return response
    
    def metadataResponseMapper(self, length) -> dict:
        return {
            'filepath': os.path.join(Config.BASE_DIR, self.filename),
            'name': self.metadata.title,
            'artist': self.metadata.artists,
            'album': self.metadata.album,
            'date': self.metadata.release_date,
            'length': length,
            'image': self.metadata.cover,
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