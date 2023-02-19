import json
from importlib_metadata import metadata
from magic import Magic
from re import M
from mutagen.id3 import (
    # Meaning of the various frames: https://mutagen.readthedocs.io/en/latest/api/id3_frames.html
    ID3, APIC, TIT2, TALB, TCON, TLAN, TRCK, TSRC, TXXX, TPE1, USLT
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
            'image': data["cover_path"],
            'track_id': data["track_id"]
        }
    
    def getmusicbrainzdata(filename, metadata_user, metadata_source, cover_source):
        logger.info('Getting Musicbrainz metadata')
        album = metadata_source["release"]["release-group"]["title"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        artist_list = []
        for artist in metadata_source["release"]["artist-credit"]:
            try:
                artist_list.append(artist["artist"]["name"])
            except Exception:
                pass
        artist_list = artist_list if json.loads(metadata_user["artists"]) == [""] else json.loads(metadata_user["artists"])
        try:
            language = metadata_source["release"]["text-representation"]["language"]
        except Exception:
            language = ""
        mbp_releaseid = metadata_source["release"]["id"] if len(metadata_user["trackid"]) < 1 else metadata_user["trackid"]
        mbp_albumid = metadata_source["release"]["release-group"]["id"] if len(metadata_user["albumid"]) < 1 else metadata_user["albumid"]
        barcode = metadata_source["release"]["barcode"] if "barcode" in metadata_source["release"] else ""
        release_date = ""
        mbp_trackid = ""
        tracknr = ""
        isrc = ""
        length = ""
        genres = ""
        cover_path = cover_source if len(metadata_user["cover"]) < 1 else metadata_user["cover"]
        magic = Magic(mime=True)
        if cover_path != os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png'):
            try:
                response = requests.get(cover_path)
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
            except Exception:               
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            cover_mime_type = "image/png"
            file = open(cover_path, 'rb')
            image = file.read()
        
        total_tracks = len(metadata_source["release"]["medium-list"][0]["track-list"])
        
        for track in metadata_source["release"]["medium-list"][0]["track-list"]:
            if metadata_source["release"]["title"] in track["recording"]["title"]:
                tracknr += track["number"] if "number" in track and len(track["number"]) > 0 else 1
                mbp_trackid += track["id"]
                isrc += track["recording"]["isrc-list"][0] if "isrc-list" in track["recording"] else ''
                length += track["recording"]["length"] if "length" in track["recording"] else ''
        genres = ""
        try:
            if "tag-list" in metadata_source["release"]["release-group"]:
                for tag in metadata_source["release"]["release-group"]["tag-list"]:
                    genres += tag['name'] + "; "
            elif 'tag-list' in metadata_source["release"]["medium-list"][0]["track-list"][int(tracknr) - 1]["recording"]:
                for tag in metadata_source["release"]["medium-list"][0]["track-list"][int(tracknr) - 1]["recording"]["tag-list"]:
                    genres += tag['name'] + "; "
        except Exception:
            pass
        genres = genres.strip()[0:len(genres.strip()) - 1]# if len(metadata_user["genres"]) < 1 else metadata_user["genres"].replace(';', '/')
        
        if "first-release-date" in metadata_source["release"]["release-group"]:
            release_date = metadata_source["release"]["release-group"]["first-release-date"] if len(metadata_user['album_releasedate']) < 1 else metadata_user["album_releasedate"]
        else:
            release_date = metadata_source["release"]["date"]
        
        title = metadata_source["release"]["title"] if len(metadata_user["title"]) < 1 else metadata_user["title"]
        data = {
            'filename': filename,
            'album': album,
            'artists': artist_list,
            'language': language,
            'track_id': mbp_releaseid,
            'album_id': mbp_albumid,
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
    
    def getspotifydata(filename, metadata_user, metadata_source):
        logger.info('Getting Spotify metadata')
        album = metadata_source["album"]["name"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        trackid = metadata_source["id"] if len(metadata_user["trackid"]) < 1 else metadata_user["trackid"]
        albumid = metadata_source["album"]["id"] if len(metadata_user["albumid"]) < 1 else metadata_user["albumid"]
        isrc = metadata_source["external_ids"].get('isrc', '')
        release_date = metadata_source["album"]["release_date"] if len(metadata_user["album_releasedate"]) < 1 else metadata_user["album_releasedate"]
        length = str(int(int(metadata_source["duration_ms"]) / 1000))
        tracknr = metadata_source["track_number"] if len(metadata_user["album_tracknr"]) < 1 else metadata_user["album_tracknr"]
        total_tracks = metadata_source["total_tracks"] if 'total_tracks' in metadata_source else '1'
        default_cover = os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png')
        cover_path = metadata_source["album"]["images"][0]["url"] if len(metadata_user["cover"]) < 1 else metadata_user["cover"]
        title = metadata_source["name"] if len(metadata_user["title"]) < 1 else metadata_user["title"]
        genres = "" # Spotify API doesn't provide genres with tracks
        spotify_artists = []
        for artist in metadata_source["artists"]:
            spotify_artists.append(artist["name"])
        print(spotify_artists)
        artists = spotify_artists if json.loads(metadata_user["artists"]) == [""] else json.loads(metadata_user["artists"])
        print(artists)
        print(metadata_user["artists"])
        if cover_path != default_cover:
            try:
                response = requests.get(cover_path)
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
            except Exception:               
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            cover_mime_type = "image/png"
            file = open(cover_path, 'rb')
            image = file.read()
        data = {
            'filename': filename,
            'album': album,
            'artists': artists,
            'barcode':  "",
            'language': "Unknown",
            'track_id': trackid,
            'album_id': albumid,
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
    
    def getdeezerdata(filename, metadata_user, metadata_source):
        album = metadata_source["album"]["title"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        trackid = str(metadata_source["id"]) if len(metadata_user["trackid"]) < 1 else str(metadata_user["trackid"])
        albumid = str(metadata_source["album"]["id"]) if len(metadata_user["albumid"]) < 1 else str(metadata_user["albumid"])
        isrc = metadata_source.get('isrc', '')
        release_date = metadata_source["release_date"] if len(metadata_user["album_releasedate"]) < 1 else metadata_user["album_releasedate"]
        length = str(metadata_source.get('duration', '0'))
        tracknr = str(metadata_source.get('track_position', 1)) if len(metadata_user["album_tracknr"]) < 1 else metadata_user["album_tracknr"]
        total_tracks = 1
        default_cover = os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png')
        cover_path = metadata_source["album"].get('cover_xl', default_cover) if len(metadata_user["cover"]) < 1 else metadata_user["cover"]
        title = metadata_source["title"] if len(metadata_user["title"]) < 1 else metadata_user["title"]
        deezer_artists = ""
        for contributor in metadata_source["contributors"]:
            if contributor["type"].lower() == 'artist':
                deezer_artists.append(contributor["name"])
        artists = deezer_artists if json.loads(metadata_user["artists"]) == [""] else json.loads(metadata_user["artists"])
        if cover_path != default_cover:
            try:
                response = requests.get(cover_path)
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
            except Exception:               
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            file = open(cover_path, 'rb')
            image = file.read()
            cover_mime_type = "image/png"
        data = {
            'filename': filename,
            'album': album,
            'artists': artists,
            'barcode':  "",
            'language': "Unknown",
            'track_id': trackid,
            'album_id': albumid,
            'release_date': release_date,
            'tracknr': tracknr,
            'total_tracks': total_tracks,
            'isrc': isrc,
            'length': length,
            'cover_path': cover_path,
            'cover_mime_type': cover_mime_type,
            'image': image,
            'title': title,
            'genres': ""
        }
        return data
    
    def getgeniusdata(filename, metadata_user, metadata_source, lyrics):
        logger.info('Getting Genius metadata')
        album = metadata_source["song"]["album"]["name"] if len(metadata_user["album"]) < 1 else metadata_user["album"]
        trackid = metadata_source["id"] if len(metadata_user["trackid"] < 1) else metadata_user["trackid"]
        albumid = metadata_source["song"]["album"]["id"] if len(metadata_user["albumid"]) < 1 else metadata_user["albumid"]
        release_date = metadata_source["song"]["release_date"] if len(metadata_user["album_releasedate"]) < 1 else metadata_user["album_releasedate"]
        length = 0
        tracknr = metadata_user["album_tracknr"]
        total_tracks = 1
        default_cover = os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png')
        cover_path = metadata_source["song"]["song_art_image_thumbnail_url"] if len(metadata_user["cover"]) < 1 else metadata_user["cover"]
        title = metadata_source["song"]["title"] if len(metadata_user["title"]) < 1 else metadata_user["title"]
        geniusartists = metadata_source["song"]["primary_artist"]["name"] + "; "
        for artist in metadata_source["song"]["featured_artists"]:
            geniusartists += artist["name"] + "; "
        artists = geniusartists[0:len(geniusartists) - 2] if len(metadata_user["artists"]) < 1 else metadata_user["artists"]
        if cover_path != default_cover:
            try:
                response = requests.get(cover_path)
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
            except Exception:               
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            cover_mime_type = "image/png"
            file = open(cover_path, 'rb')
            image = file.read()
    
        data = {
            'filename': filename,
            'album': album,
            'artists': artists,
            'barcode':  "",
            'language': "Unknown",
            'track_id': trackid,
            'album_id': albumid,
            'release_date': release_date,
            'tracknr': tracknr,
            'total_tracks': total_tracks,
            'isrc': "",
            'length': length,
            'cover_path': cover_path,
            'cover_mime_type': cover_mime_type,
            'image': image,
            'title': title,
            'genres': "",
            'lyrics': lyrics
        }
        return data
    
    def onlyuserdata(filename, metadata_user):
        if metadata_user["cover"] != '':
            try:
                cover_path = metadata_user["cover"]
                response = requests.get(metadata_user["cover"])
                image = response.content
                magic = Magic(mime=True)
                cover_mime_type = magic.from_buffer(image)
            except Exception:
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            cover_path = os.path.join(Config.BASE_DIR, 'metatube/static/images/empty_cover.png')
            file = open(cover_path, 'rb')
            image = file.read()
            cover_mime_type = "image/png"
        
        data = {
            'filename': filename,
            'album': metadata_user.get('album', ''),
            'artists': metadata_user.get('artists', ''),
            'barcode': "",
            'language': "Unknown",
            'track_id': metadata_user.get('trackid', ''),
            'album_id': metadata_user.get('albumid', ''),
            'release_date': metadata_user.get('album_releasedate', ''),
            'tracknr': metadata_user.get('album_tracknr', '1'),
            'total_tracks': metadata_user.get('album_tracknr', '1'),
            'isrc': "",
            'length': "",
            'cover_path': cover_path,
            'cover_mime_type': cover_mime_type,
            'image': image,
            'title': metadata_user.get('title', ''),
            'genres': ""
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
            if data.get('source', '') == 'Spotify':
                audio.RegisterTXXXKey('spotify_trackid', data["track_id"])
                audio.RegisterTXXXKey('spotify_albumid', data["album_id"])
            elif data.get('source', '') == 'Deezer':
                audio.RegisterTXXXKey('deezer_trackid', data["track_id"])
                audio.RegisterTXXXKey('deezer_albumid', data["album_id"])
                
            if 'lyrics' in data:
                audio.RegisterTextKey('lyrics', "USLT")
            
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
        audio["tracknumber"] = str(data["tracknr"])
        audio["title"] = data["title"]
        audio["date"] = data["release_date"]
        audio["genre"] = data["genres"]
        if 'lyrics' in data and data["extension"] != 'MP3':
            audio['lyrics'] = data['lyrics']
        if data.get('source', '') == 'Musicbrainz':
            audio["musicbrainz_releasetrackid"] = data["track_id"]
            audio["musicbrainz_releasegroupid"] = data["album_id"]
            audio["musicbrainz_albumid"] = data["album_id"]
        
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
        dateobj = datetime.strptime(data["release_date"], '%Y-%m-%d') if len(data["release_date"]) > 0 else datetime.now().date()
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
        
        response = {
            'title': audio.get('title', [''])[0],
            'artists': audio.get('artist', [''])[0],
            'album': audio.get('album', [''])[0],
            'barcode': audio.get('barcode', [''])[0],
            'genres': audio.get('genre', [''])[0],
            'language': audio.get('language', [''])[0],
            'release_date': audio.get('date', [''])[0],
            'album_id': "",
            'total_tracks': "",
            'mbp_releaseid': audio.get('musicbrainz_releasetrackid', [''])[0],
            'mbp_releasegroupid': audio.get('musicbrainz_releasegroupid', [''])[0],
            'isrc': audio.get('isrc', [''])[0],
            'tracknr': audio.get('tracknumber', [''])[0],
            'date': audio.get('date', [''])[0],
            'length': data.info.length,
            'bitrate': data.info.bitrate,
            'output_folder': os.path.dirname(filename),
            'filename': filename,
            "goal": "edit",
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
            'title': video.get('\xa9nam', [''])[0],
            'album': video.get("\xa9alb", [''])[0],
            'artists': video.get("\xa9ART", [''])[0],
            'genres': video.get("\xa9gen", [''])[0],
            'release_date': video.get("\xa9day", [''])[0],
            'bitrate': bitrate,
            'output_folder': os.path.dirname(filename),
            'filename': filename,
            'length': video.info.length,
            'tracknr': video.get('trkn', [[1]])[0][0]
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