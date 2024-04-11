import json
from metatube.spotify import spotify_metadata as Spotify
from metatube.genius import Genius
from re import M
from metatube import Config as env, logger
from metatube import musicbrainz
from metatube.deezer import Deezer
from metatube.database import Config
from .metadataObject import MetadataObject
from .readMetadata import readMetadata
from .MetadataExceptions import (
    InvalidCoverURL,
    NoMetadataAPIResult,
    NoMetadataFound,
    NoSpotifyCredentails,
    InvalidSpotifyCredentials,
    NoGeniusToken,
    InvalidGeniusToken
)    

class processMetadata(object):  
    def __init__(self, usermetadata, extension):
        self.usermetadata = usermetadata
        self.songid = usermetadata['songid'] or None
        self.source = usermetadata['metadata_source'] or None
        self.cover = usermetadata['cover_source']
        self.extension = extension
        
        
    def getMetadata(self, app) -> MetadataObject:
        metadata = None
        if self.source == 'Spotify':
            with app.app_context():
                cred = Config.get_spotify()
                if str(cred) == '':
                    raise NoSpotifyCredentails("Spotify was selected as source, however there are no API credentials for the Spotify API.")
            try:
                spotify = Spotify(cred.split(';')[1], cred.split(';')[0])
            except InvalidSpotifyCredentials as exception:
                raise exception from exception
            metadata_source = spotify.fetch_track(self.songid) # type: ignore
            if metadata_source is None:
                raise NoMetadataAPIResult("There was no result from the Spotify API.")
            metadata = self.getspotifydata(metadata_source)
        elif self.source == 'Musicbrainz':
            metadata_source = musicbrainz.search_id_release(self.songid)
            if metadata_source is None:
                raise NoMetadataAPIResult("There was no result from the Musicbrainz API.")
            metadata = self.getmusicbrainzdata(metadata_source)
        elif self.source == 'Deezer':
            metadata_source = Deezer.searchid(self.songid) # type: ignore
            if metadata_source is None:
                raise NoMetadataAPIResult("There was no result from the Deezer API.")
            metadata = self.getdeezerdata(metadata_source)
        elif self.source == 'Genius':
            token = Config.get_genius()
            if str(token) == '':
                raise NoGeniusToken("Genius was selected as source, however there is no API token for the Genius API.")
            try:
                genius = Genius(token)
                metadata_source = genius.fetchsong(self.songid) # type: ignore
            except Exception:
                raise InvalidGeniusToken("Invalid Genius API token.")
            if metadata_source is None:
                raise NoMetadataAPIResult("There was no result from the selected metadata API.")
            lyrics = genius.fetchlyrics(metadata_source["song"]["url"]) # type: ignore
            metadata = self.getgeniusdata(metadata_source, lyrics)
        else:
            metadata = self.onlyuserdata()
        if metadata is None:
            raise NoMetadataFound("No metadata has been found from either the user input or the selected metadata API.")
        return metadata
            
    def getmusicbrainzdata(self, metadata_source) -> MetadataObject | None:
        logger.info('Getting Musicbrainz metadata')
        album = metadata_source["release"]["release-group"]["title"] if len(self.usermetadata["album"]) < 1 else self.usermetadata["album"]
        artist_list = []
        for artist in metadata_source["release"]["artist-credit"]:
            try:
                artist_list.append(artist["artist"]["name"])
            except Exception:
                pass
        artist_list = artist_list if json.loads(self.usermetadata["artists"]) == [""] else json.loads(self.usermetadata["artists"])
        try:
            language = metadata_source["release"]["text-representation"]["language"]
        except Exception:
            language = ""
        mbp_songid = metadata_source["release"]["id"] if len(self.usermetadata["songid"]) < 1 else self.usermetadata["songid"]
        mbp_albumid = metadata_source["release"]["release-group"]["id"] if len(self.usermetadata["albumid"]) < 1 else self.usermetadata["albumid"]
        release_date = ""
        mbp_songid = ""
        tracknr = ""
        isrc = ""
        genres = ""
        cover_path = self.cover if len(self.usermetadata["cover"]) < 1 else self.usermetadata["cover"]
        try:
            imagedata = readMetadata.getImage(cover_path)
        except InvalidCoverURL as e:
            raise e from e
        
        for track in metadata_source["release"]["medium-list"][0]["track-list"]:
            if metadata_source["release"]["title"] in track["recording"]["title"]:
                tracknr += track["number"] if "number" in track and len(track["number"]) > 0 else 1 # type: ignore
                mbp_songid += track["id"]
                isrc += track["recording"]["isrc-list"][0] if "isrc-list" in track["recording"] else ''
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
        genres = genres.strip()[0:len(genres.strip()) - 1]# if len(self.usermetadata["genres"]) < 1 else self.usermetadata["genres"].replace(';', '/')
        
        if "first-release-date" in metadata_source["release"]["release-group"]:
            release_date = metadata_source["release"]["release-group"]["first-release-date"] if len(self.usermetadata['album_releasedate']) < 1 else self.usermetadata["album_releasedate"]
        else:
            release_date = metadata_source["release"]["date"]
        
        title = metadata_source["release"]["title"] if len(self.usermetadata["title"]) < 1 else self.usermetadata["title"]
        
        return MetadataObject(
            title,
            ';'.join(artist_list),
            album,
            genres,
            language,
            release_date,
            mbp_songid,
            mbp_albumid,
            int(tracknr),
            imagedata['image'],
            cover_path,
            imagedata['mime_type'],
            isrc,
            '',
            self.extension,
            'musicbrainz'
        )
    
    def getspotifydata(self, metadata_source) -> MetadataObject | None:
        logger.info('Getting Spotify metadata')
        album = metadata_source["album"]["name"] if len(self.usermetadata["album"]) < 1 else self.usermetadata["album"]
        songid = metadata_source["id"] if len(self.usermetadata["songid"]) < 1 else self.usermetadata["songid"]
        albumid = metadata_source["album"]["id"] if len(self.usermetadata["albumid"]) < 1 else self.usermetadata["albumid"]
        isrc = metadata_source["external_ids"].get('isrc', '')
        release_date = metadata_source["album"]["release_date"] if len(self.usermetadata["album_releasedate"]) < 1 else self.usermetadata["album_releasedate"]
        tracknr = metadata_source["track_number"] if len(self.usermetadata["album_tracknr"]) < 1 else self.usermetadata["album_tracknr"]
        cover_path = metadata_source["album"]["images"][0]["url"] if len(self.usermetadata["cover"]) < 1 else self.usermetadata["cover"]
        title = metadata_source["name"] if len(self.usermetadata["title"]) < 1 else self.usermetadata["title"]
        genres = "" # Spotify API doesn't provide genres with tracks
        spotify_artists = []
        for artist in metadata_source["artists"]:
            spotify_artists.append(artist["name"])
        artists = spotify_artists if json.loads(self.usermetadata["artists"]) == [""] else json.loads(self.usermetadata["artists"])
        try:
            imagedata = readMetadata.getImage(cover_path)
        except InvalidCoverURL as e:
            raise e from e
            
        return MetadataObject(
            title,
            ';'.join(artists),
            album,
            genres,
            'Unknown',
            release_date,
            songid,
            albumid,
            int(tracknr),
            imagedata['image'],
            cover_path,
            imagedata['mime_type'],
            isrc,
            '',
            self.extension,
            'spotify',
        )
    
    def getdeezerdata(self, metadata_source) -> MetadataObject | None:
        album = metadata_source["album"]["title"] if len(self.usermetadata["album"]) < 1 else self.usermetadata["album"]
        songid = str(metadata_source["id"]) if len(self.usermetadata["songid"]) < 1 else str(self.usermetadata["songid"])
        albumid = str(metadata_source["album"]["id"]) if len(self.usermetadata["albumid"]) < 1 else str(self.usermetadata["albumid"])
        isrc = metadata_source.get('isrc', '')
        release_date = metadata_source["release_date"] if len(self.usermetadata["album_releasedate"]) < 1 else self.usermetadata["album_releasedate"]
        tracknr = str(metadata_source.get('track_position', 1)) if len(self.usermetadata["album_tracknr"]) < 1 else self.usermetadata["album_tracknr"]
        default_cover = env.DEFAULT_COVER_PATH
        cover_path = metadata_source["album"].get('cover_xl', default_cover) if len(self.usermetadata["cover"]) < 1 else self.usermetadata["cover"]
        title = metadata_source["title"] if len(self.usermetadata["title"]) < 1 else self.usermetadata["title"]
        deezer_artists = []
        for contributor in metadata_source["contributors"]:
            if contributor["type"].lower() == 'artist':
                deezer_artists.append(contributor["name"])
        artists = deezer_artists if json.loads(self.usermetadata["artists"]) == [""] else json.loads(self.usermetadata["artists"])
        try:
            imagedata = readMetadata.getImage(cover_path)
        except InvalidCoverURL as e:
            raise e from e
            
        return MetadataObject(
            title,
            ';'.join(artists),
            album,
            '',
            'Unknown',
            release_date,
            songid,
            albumid,
            int(tracknr),
            imagedata['image'],
            cover_path,
            imagedata['mime_type'],
            isrc,
            '',
            self.extension,
            'deezer',
        )
    
    def getgeniusdata(self, metadata_source, lyrics) -> MetadataObject | None:
        logger.info('Getting Genius metadata')
        album = metadata_source["song"]["album"]["name"] if len(self.usermetadata["album"]) < 1 else self.usermetadata["album"]
        songid = metadata_source["id"] if len(self.usermetadata["songid"] < 1) else self.usermetadata["songid"]
        albumid = metadata_source["song"]["album"]["id"] if len(self.usermetadata["albumid"]) < 1 else self.usermetadata["albumid"]
        release_date = metadata_source["song"]["release_date"] if len(self.usermetadata["album_releasedate"]) < 1 else self.usermetadata["album_releasedate"]
        genres = ''
        language = 'Unknown'
        tracknr = self.usermetadata["album_tracknr"]
        cover_path = metadata_source["song"]["song_art_image_thumbnail_url"] if len(self.usermetadata["cover"]) < 1 else self.usermetadata["cover"]
        title = metadata_source["song"]["title"] if len(self.usermetadata["title"]) < 1 else self.usermetadata["title"]
        geniusartists = metadata_source["song"]["primary_artist"]["name"] + "; "
        for artist in metadata_source["song"]["featured_artists"]:
            geniusartists += artist["name"] + "; "
        artists = geniusartists[0:len(geniusartists) - 2] if len(self.usermetadata["artists"]) < 1 else self.usermetadata["artists"]
        try:
            imagedata = readMetadata.getImage(cover_path)
        except InvalidCoverURL as e:
            raise e from e
            
        return MetadataObject(
            title,
            artists,
            album,
            genres,
            language,
            release_date,
            songid,
            albumid,
            int(tracknr),
            imagedata['image'],
            cover_path,
            imagedata['mime_type'],
            '',
            lyrics,
            self.extension,
            'genius',
        )
    
    def onlyuserdata(self) -> MetadataObject | None:
        try:
            imagedata = readMetadata.getImage(self.usermetadata["cover"])
        except InvalidCoverURL as e:
            raise e from e
            
        return MetadataObject(
            self.usermetadata.get('title', ''),
            self.usermetadata.get('artists', ''),
            self.usermetadata.get('album', ''),
            '',
            'Unknown',
            self.usermetadata.get('album_releasedate', ''),
            self.usermetadata.get('songid', ''),
            self.usermetadata.get('albumid', ''),
            self.usermetadata.get('album_tracknr', '1'),
            imagedata['image'],
            self.usermetadata["cover"],
            imagedata['mime_type'],
            '',
            '',
            self.extension,
            'user'
        )