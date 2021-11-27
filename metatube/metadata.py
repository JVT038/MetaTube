import mutagen
from mimetypes import guess_type
from mutagen.id3 import ID3, TIT2, APIC
from mutagen.mp3 import EasyMP3
from mutagen.easyid3 import EasyID3
from PIL import Image
import requests
from io import BytesIO


class MetaData:    
    def getdata(filename, metadata_user, metadata_mbp, cover_mbp):
        album = metadata_mbp["release"]["release-group"]["title"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        artist_list = ""
        for artist in metadata_mbp["release"]["artist-credit"]:
            try:
                artist_list += artist["artist"]["name"] + "/ "
            except:
                pass
        artist_list = artist_list.strip()[0:len(artist_list.strip()) - 1] if len(metadata_user["artists"]) < 1 else metadata_user["artists"]
        language = metadata_mbp["release"]["text-representation"]["language"]
        mbp_releaseid = metadata_mbp["release"]["id"] if len(metadata_user["mbp_releaseid"]) < 1 else metadata_user["mbp_releaseid"]
        mbp_albumid = metadata_mbp["release"]["release-group"]["id"] if len(metadata_user["mbp_albumid"]) < 1 else metadata_user["mbp_albumid"]
        barcode = metadata_mbp["release"]["barcode"]
        release_date = ""
        mbp_trackid = ""
        tracknr = ""
        isrc = ""
        length = ""
        cover_path = cover_mbp["images"][0]["image"] if len(metadata_user['cover']) < 1 else metadata_user['cover']
        mime_type = guess_type(cover_path)
        response = requests.get(cover_path)
        image = response.content
        
        for track in metadata_mbp["release"]["medium-list"][0]["track-list"]:
            if metadata_mbp["release"]["title"] in track["recording"]["title"]:
                tracknr += track["number"]
                mbp_trackid += track["id"]
                isrc += track["recording"]["isrc-list"][0]
                length += track["recording"]["length"]
        
        if metadata_mbp["release"]["release-group"]["type"] == 'Album':
            release_date = metadata_mbp["release"]["release-group"]["first-release-date"] if len(metadata_user['album_releasedate']) < 1 else metadata_user["album_releasedate"]
        else:
            release_date = metadata_mbp["release"]["date"]
        
        title = metadata_mbp["release"]["title"] if len(metadata_user["title"]) < 1 else metadata_user["title"]
        data = {
            'filename': filename,
            'album': album,
            'artists': artist_list,
            'language': language,
            'mbp_releaseid': mbp_releaseid,
            'mbp_albumid': mbp_albumid,
            'mbp_trackid': mbp_trackid,
            'barcode': barcode,
            'release_date': release_date,
            'tracknr': tracknr,
            'isrc': isrc,
            'length': length,
            'cover_path': cover_path,
            'mime_type': mime_type,
            'image': image,
            'title': title
        }
        return data
    def MP3(data):
        '''
        Valid fields:
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
            "musicbrainz_trackid",
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
            "musicbrainz_releasetrackid",
            "musicbrainz_releasegroupid",
            "musicbrainz_workid",
            "acoustid_fingerprint",
            "acoustid_id"
        '''        
        audio = EasyID3(data["filename"])
        audio["album"] = data["album"]
        audio["artist"] = data["artists"]
        audio["barcode"] = data["barcode"]
        audio["language"] = data["language"]
        audio["tracknumber"] = data["tracknr"]
        audio["title"] = data["title"]
        audio["musicbrainz_releasetrackid"] = data["mbp_releaseid"]
        audio["musicbrainz_releasegroupid"] = data["mbp_albumid"]
        audio["musicbrainz_albumid"] = data["mbp_albumid"]
        audio["musicbrainz_albumtype"] = 'album'
        audio["date"] = data["release_date"]
        
        audio.save()
        print('Metadata added')
        
        cover = ID3(data["filename"])
        cover["APIC"] = APIC(
            encoding=3,
            mime=data["mime_type"],
            type=3,
            desc=u'Cover',
            data=data["image"]
        )
        cover.save()
        print('cover added')
    
    def OggVorbisFlac(filename):
        pass
    
    def AAC(filename):
        pass
    
    def FLAC(filename):
        pass
    
    def M4A(filename):
        pass
    
    def OPUS(filename):
        pass
    
    def WAV(filename):
        pass
    
    def MP4(filename):
        pass
    
    def FLV(filename):
        pass
    
    def WEBM(filename):
        pass
    
    def MKV(filename):
        pass
    
    def AVI(filename):
        pass
    
    def addmetadata(filename, extension, release_id):
        getattr(MetaData, extension.upper())()