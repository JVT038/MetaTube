from mimetypes import guess_type
from mutagen.id3 import (
    # Meaning of the various frames: https://mutagen.readthedocs.io/en/latest/api/id3_frames.html
    ID3, APIC, TIT2, TALB, TCON, TLAN, TRCK, TSRC, TXXX, TPE1
)
from mutagen.flac import FLAC, Picture
from mutagen.aac import AAC
from mutagen.wave import WAVE
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4, MP4Cover
from metatube import sockets, Config, logger
from datetime import datetime
import requests, base64, os

class MetaData:
    def getresponse(data):
        return {
            'filepath': os.path.join(Config.BASE_DIR, data["filename"]),
            'name': data["title"],
            'artist': data["artists"],
            'album': data["album"],
            'date': data["release_date"],
            'length': data["length"],
            'image': data["image"],
            'musicbrainz_id': data["mbp_releaseid"]
        }
    
    def getdata(filename, metadata_user, metadata_mbp, cover_mbp):
        album = metadata_mbp["release"]["release-group"]["title"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        artist_list = ""
        for artist in metadata_mbp["release"]["artist-credit"]:
            try:
                artist_list += artist["artist"]["name"] + "/ "
            except Exception:
                pass
        artist_list = artist_list.strip()[0:len(artist_list.strip()) - 1] if len(metadata_user["artists"]) < 1 else metadata_user["artists"]
        try:
            language = metadata_mbp["release"]["text-representation"]["language"]
        except Exception:
            language = ""
        mbp_releaseid = metadata_mbp["release"]["id"] if len(metadata_user["mbp_releaseid"]) < 1 else metadata_user["mbp_releaseid"]
        mbp_albumid = metadata_mbp["release"]["release-group"]["id"] if len(metadata_user["mbp_albumid"]) < 1 else metadata_user["mbp_albumid"]
        barcode = metadata_mbp["release"]["barcode"] if "barcode" in metadata_mbp["release"] else ""
        release_date = ""
        mbp_trackid = ""
        tracknr = ""
        isrc = ""
        length = ""
        genres = ""
        if len(metadata_user["cover"]) > 0:
            cover_path = metadata_user["cover"]
        elif cover_mbp != 'None':
            cover_path = cover_mbp["images"][0]["image"]
        else:
            cover_path = os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png')
        cover_mime_type = guess_type(cover_path)[0]
        if cover_path != os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png'):
            try:
                response = requests.get(cover_path)
                image = response.content
            except Exception:               
                sockets.searchvideo('Cover URL is invalid')
                return False
        else:
            file = open(cover_path, 'rb')
            image = file.read()
        
        total_tracks = len(metadata_mbp["release"]["medium-list"][0]["track-list"])
        
        for track in metadata_mbp["release"]["medium-list"][0]["track-list"]:
            if metadata_mbp["release"]["title"] in track["recording"]["title"]:
                tracknr += track["number"] if "number" in track and len(track["number"]) > 0 else 1
                mbp_trackid += track["id"]
                isrc += track["recording"]["isrc-list"][0] if "isrc-list" in track["recording"] else ''
                length += track["recording"]["length"] if "length" in track["recording"] else ''
        genres = ""
        if "tag-list" in metadata_mbp["release"]["release-group"]:
            for tag in metadata_mbp["release"]["release-group"]["tag-list"]:
                genres += tag['name'] + "; "
        elif 'tag-list' in metadata_mbp["release"]["medium-list"][0]["track-list"][int(tracknr) - 1]["recording"]:
            for tag in metadata_mbp["release"]["medium-list"][0]["track-list"][int(tracknr) - 1]["recording"]["tag-list"]:
                genres += tag['name'] + "; "
        genres = genres.strip()[0:len(genres.strip()) - 1]# if len(metadata_user["genres"]) < 1 else metadata_user["genres"].replace(';', '/')
        
        if "first-release-date" in metadata_mbp["release"]["release-group"]:
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
            'total_tracks': total_tracks,
            'isrc': isrc,
            'length': length,
            'cover_path': cover_path,
            'cover_mime_type': cover_mime_type,
            'image': image,
            'title': title,
            'genres': genres
        }
        return data
        
    def mergeaudiodata(data):
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
        if data["extension"] == 'MP3':
            audio = EasyID3(data["filename"])
        elif data["extension"] == 'FLAC':
            audio = FLAC(data["filename"])
        elif data["extension"] == 'AAC':
            audio = AAC(data["filename"])
        elif data["extension"] == 'OPUS':
            audio = OggOpus(data["filename"])
        elif data["extension"] == 'OGG':
            audio = OggVorbis(data["filename"])
            
        
        audio["album"] = data["album"]
        audio["artist"] = data["artists"]
        audio["barcode"] = data["barcode"]
        audio["language"] = data["language"]
        audio["tracknumber"] = data["tracknr"]
        audio["title"] = data["title"]
        audio["musicbrainz_releasetrackid"] = data["mbp_releaseid"]
        audio["musicbrainz_releasegroupid"] = data["mbp_albumid"]
        audio["musicbrainz_albumid"] = data["mbp_albumid"]
        audio["date"] = data["release_date"]
        audio["genre"] = data["genres"]
        
        audio.save()
        
        if data["extension"] == 'MP3':
            cover = ID3(data["filename"])
            cover["APIC"] = APIC(
                encoding=3,
                mime=data["cover_mime_type"],
                type=3,
                desc=u'Cover',
                data=data["image"]
            )
            cover.save()
        else:
            cover = Picture()
            cover.data = data["image"]
            cover.type = 3
            cover.mime = data["cover_mime_type"]
            cover.desc = 'Front cover'
            if data["extension"] == 'FLAC':
                audio.add_picture(cover)
            else:
                cover_data = cover.write()
                audio["metadata_block_picture"] = [base64.b64encode(cover_data).decode('ascii')]
                audio.save()
        response = MetaData.getresponse(data)
        if data["goal"] == 'edit':
            response["itemid"] = data["itemid"]
            logger.info('Finished changing metadata of %s', data["title"])
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif data["goal"] == 'add':
            logger.info('Finished adding metadata to %s', data["title"])
            sockets.downloadprogress({'status':'finished_metadata', 'data': response})
                
    def mergeid3data(data):
        if data["extension"] == 'WAV':
            audio = WAVE(data["filename"])
        try:
            audio.add_tags()
        except Exception:
            pass
        audio.tags.add(TIT2(encoding=3, text=data["title"]))
        audio.tags.add(TALB(encoding=3, text=data["album"]))
        audio.tags.add(TCON(encoding=3, text=data["genres"]))
        audio.tags.add(TLAN(encoding=3, text=data["language"]))
        audio.tags.add(TRCK(encoding=3, text=data["tracknr"]))
        audio.tags.add(TSRC(encoding=3, text=data["isrc"]))
        audio.tags.add(TPE1(encoding=3, text=data["artists"]))
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_releasetrackid', text=data["mbp_releaseid"]))
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_releasegroupid', text=data['mbp_albumid']))
        audio.tags.add(TXXX(encoding=3, desc=u'musicbrainz_albumid', text=data["mbp_albumid"]))
        audio.tags.add(APIC(encoding=3, mime=data["cover_mime_type"], type=3, desc=u'Cover', data=data["image"]))
        
        response = MetaData.getresponse(data)
        if data["goal"] == 'edit':
            response["itemid"] = data["itemid"]
            logger.info('Finished changing metadata of %s', data["title"])
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif data["goal"] == 'add':
            logger.info('Finished adding metadata to %s', data["title"])
            sockets.downloadprogress({'status':'finished_metadata', 'data': response})
    def mergevideodata(data):
        if data["extension"] in ['M4A', 'MP4']:
            video = MP4(data["filename"])
        dateobj = datetime.strptime(data["release_date"], '%Y-%m-%d')
        year = dateobj.year
        # iTunes metadata list / key values: https://mutagen.readthedocs.io/en/latest/api/mp4.html?highlight=M4A#mutagen.mp4.MP4Tags
        video["\xa9nam"] = data["title"]
        video["\xa9alb"] = data["album"]
        video["\xa9ART"] = data["artists"]
        video["\xa9gen"] = data["genres"]
        video["\xa9day"] = str(year)
        try:
            video["trkn"] = [(int(data["tracknr"]), int(data["total_tracks"]))]
        except Exception:
            pass
        imageformat = MP4Cover.FORMAT_PNG if "png" in data["cover_mime_type"] else MP4Cover.FORMAT_JPEG
        video["covr"] = [MP4Cover(data["image"], imageformat)]
        
        video.save()
        response = MetaData.getresponse(data)
        
        if data["goal"] == 'edit':
            response["itemid"] = data["itemid"]
            logger.info('Finished changing metadata of %s', data["title"])
            sockets.overview({'msg': 'changed_metadata', 'data': response})
        elif data["goal"] == 'add':
            logger.info('Finished adding metadata to %s', data["title"])
            sockets.downloadprogress({'status':'finished_metadata', 'data': response})
    
    def readaudiometadata(filename):
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension == 'MP3':
            audio = EasyID3(filename)
            data = MP3(filename)
            bitrate = data.info.bitrate
            length = data.info.length
        elif extension == 'FLAC':
            audio = FLAC(filename)
        elif extension == 'AAC':
            audio = AAC(filename)
        elif extension == 'OPUS':
            audio = OggOpus(filename)
        elif extension == 'OGG':
            audio = OggVorbis(filename)
            
        try:
            genres = audio["genre"][0]
        except Exception:
            genres = ""
        try:
            isrc = audio["isrc"][0]
        except Exception:
            isrc = ""
        try:
            tracknr = audio["tracknumber"][0]
        except Exception:
            tracknr = 1
        try:
            language = audio["language"][0]
        except Exception:
            language = ""
        
        response = {
            'title': audio["title"][0],
            'artist': audio["artist"][0],
            'album': audio["album"][0],
            'genres': genres,
            'language': language,
            'mbp_releaseid': audio["musicbrainz_releasetrackid"][0],
            'mbp_releasegroupid': audio["musicbrainz_releasegroupid"][0],
            'isrc': isrc,
            'tracknr': tracknr,
            'date': audio["date"][0],
            'length': length,
            'bitrate': bitrate,
            'output_folder': os.path.dirname(filename),
            'filepath': filename
        }
        
        return response
    
    def readvideometadata(filename):
        extension = filename.split('.')[len(filename.split('.')) - 1].upper()
        if extension in ['M4A', 'MP4']:
            video = MP4(filename)
        # Bitrate calculation: https://www.reddit.com/r/headphones/comments/3xju4s/comment/cy5dn8h/?utm_source=share&utm_medium=web2x&context=3
        # Mutagen MP4 stream info: https://mutagen.readthedocs.io/en/latest/api/mp4.html#mutagen.mp4.MP4Info
        bitrate = int(video.info.bits_per_sample * video.info.sample_rate * video.info.channels)
        response = {
            'title': video["\xa9nam"][0],
            'album': video["\xa9alb"][0],
            'artist': video["\xa9ART"][0],
            'genres': video["\xa9gen"][0],
            'bitrate': bitrate,
            'output_folder': os.path.dirname(filename),
            'filepath': filename
        }
        return response
    
    def FLV(filename):
        pass
    
    def WEBM(filename):
        pass
    
    def MKV(filename):
        pass
    
    def AVI(filename):
        pass