from metatube.overview import bp
from metatube.database import *
from mimetypes import guess_type
from metatube.youtube import YouTube as yt
from metatube.metadata import MetaData
from metatube.deezer import Deezer
from metatube.spotify import spotify_metadata as Spotify
from metatube import socketio, sockets
from metatube import Config as env
from flask import render_template
from datetime import datetime
from threading import Thread
from dateutil import parser
from distutils.util import strtobool
from shutil import move
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
import json
import os
import asyncio
import requests

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    records = Database.getrecords()
    metadata_sources = Config.get_metadata_sources()
    metadataform = render_template('metadataform.html', metadata_sources=metadata_sources)
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path, records=records, metadataview=metadataform)

@socketio.on('ytdl_search')
def search(query):
    if query is not None and len(query) > 1:
        if yt.is_supported(query):
            verbose = strtobool(str(env.LOGGER))
            video = yt.fetch_url(query, verbose)
            if Database.checkyt(video["id"]) is None:
                templates = Templates.fetchalltemplates()
                defaulttemplate = Templates.searchdefault()
                metadata_sources = Config.get_metadata_sources()
                socketio.start_background_task(yt.fetch_video, video, templates, metadata_sources, defaulttemplate)
            else:
                sockets.searchvideo('This video has already been downloaded!')
        else:
            asyncio.run(yt.search(query))
    else:
        sockets.searchvideo('Enter an URL!')
        
        
@socketio.on('ytdl_template')
def filename(data):
    info_dict = json.loads(data["info_dict"])
    filename = yt.verifytemplate(data["template"], info_dict, False)
    sockets.filenametemplate(filename)

@socketio.on('searchmetadata')
def searchmetadata(data):
    sources = Config.get_metadata_sources()
    data["max"] = Config.get_max()
    if 'musicbrainz' in sources:
        Thread(target = musicbrainz.webui, args=(data, )).start()
    if 'spotify' in sources:
        cred = Config.get_spotify().split(';')
        Thread(target = Spotify.searchspotify, args=(data, cred, )).start()
    if 'deezer' in sources:
        Thread(target = Deezer.socketsearch, args=(data, )).start()

@socketio.on('ytdl_download')
def download(data):
    url = data["url"]
    ext = data["ext"] or 'mp3'
    output_folder = data["output_folder"] or '/downloads'
    output_type = data["type"] or 'Audio'
    output_format = data["output_format"] or f'%(title)s.%(ext)s'
    bitrate = data["bitrate"] or '192'
    skipfragments = data["skipfragments"] or {}
    proxy_data = data["proxy_data"] or {'proxy_type': 'None'}
    
    width = data["width"] or 1920
    height = data["height"] or 1080
    ffmpeg = Config.get_ffmpeg()
    hw_transcoding = Config.get_hwt()
    vaapi_device = hw_transcoding.split(';')[1] if 'vaapi' in hw_transcoding else ''
    verbose = strtobool(str(env.LOGGER))
    logger.info('Request to download %s', data["url"])
    ytdl_options = yt.get_options(url, ext, output_folder, output_type, output_format, bitrate, skipfragments, proxy_data, ffmpeg, hw_transcoding, vaapi_device, width, height, verbose)
    if ytdl_options is not False:
        yt_instance = yt()
        yt_instance.get_video(url, ytdl_options)
    return 'OK'

@socketio.on('fetchmbprelease')
def fetchmbprelease(release_id):
    logger.info('Request for musicbrainz release with id %s', release_id)
    mbp = musicbrainz.search_id_release(release_id)
    socketio.emit('foundmbprelease', json.dumps(mbp))

@socketio.on('fetchmbpalbum')
def fetchmbpalbum(album_id):
    logger.info('Request for musicbrainz release group with id %s', album_id)
    mbp = musicbrainz.search_id_release_group(album_id)
    if type(mbp) != str:
        socketio.emit('foundmbpalbum', json.dumps(mbp))
    else:
        sockets.metadatalog('Release group not found!')
        
@socketio.on('fetchspotifyalbum')
def fetchspotifyalbum(input_id):
    logger.info('Request for Spotify album with id %s', input_id)
        
@socketio.on('fetchspotifytrack')
def fetchspotifytrack(input_id):
    logger.info('Request for Spotify track with id %s', input_id)
    cred = Config.get_spotify().split(';')
    spotify = Spotify(cred[1], cred[0])
    spotify.sockets_track(input_id)
    
@socketio.on('fetchdeezertrack')
def fetchdeezertrack(input_id):
    logger.info('Request for Deezer track with id %s', input_id)
    Deezer.sockets_track(input_id)

@socketio.on('mergedata')
def mergedata(filepath, release_id, metadata, cover, source):
    if Database.checktrackid(release_id) is None and Database.checktrackid(metadata.get('trackid', '')) is None:
        
        metadata_user = metadata
        cover_source = cover if cover != '/static/images/empty_cover.png' else os.path.join(env.BASE_DIR, 'metatube', cover)
        extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
        if extension in ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV']:
            if source == 'Spotify':
                cred = Config.get_spotify().split(';')
                spotify = Spotify(cred[1], cred[0])
                metadata_source = spotify.fetch_track(release_id)
                data = MetaData.getspotifydata(filepath, metadata_user, metadata_source)
            elif source == 'Musicbrainz':
                metadata_source = musicbrainz.search_id_release(release_id)
                data = MetaData.getmusicbrainzdata(filepath, metadata_user, metadata_source, cover_source)
            elif source == 'Deezer':
                metadata_source = Deezer.searchid(release_id)
                data = MetaData.getdeezerdata(filepath, metadata_user, metadata_source)
            elif source == 'Unavailable':
                data = MetaData.onlyuserdata(filepath, metadata_user)
            if data is not False:
                data["goal"] = 'add'
                data["extension"] = extension
                data["source"] = source
                if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
                    MetaData.mergeaudiodata(data)
                elif extension in ['MP4', 'M4A']:
                    MetaData.mergevideodata(data)
                elif extension in ['WAV']:
                    MetaData.mergeid3data(data)
        else:
            # The name will be the filename of the downloaded file without the extension
            filename = os.path.split(filepath)[1]
            name = filename[0:len(filename) - len(filename.split('.')[len(filename.split('.')) - 1]) - 1]
            data = {
                'filepath': filepath,
                'name': name,
                'artist': metadata_user.get('artists', 'Unknown'),
                'album': 'Unknown',
                'date': datetime.now().strftime('%d-%m-%Y'),
                'length': 'Unknown',
                'image': cover_source,
                'track_id': release_id
            }
            sockets.downloadprogress({'status': 'metadata_unavailable', 'data': data})
            logger.debug('Metadata unavailable for file %s', data["filepath"])
    else:
        sockets.searchvideo(f'{source} item has already been downloaded!')
        try:
            os.unlink(filepath)
        except Exception:
            pass
        
@socketio.on('insertitem')
def insertitem(data):
    id = Database.insert(data)
    data["id"] = id
    sockets.overview({'msg': 'inserted_song', 'data': data})
    
@socketio.on('updateitem')
def updateitem(data):
    id = data["itemid"]
    head, tail = os.path.split(data["filepath"])
    if tail.startswith('tmp_'):
        data["filepath"] = os.path.join(head, tail[4:len(tail)])
    try:
        data["date"] = parser.parse(data["date"])
    except Exception:
        data["date"] = datetime.now().date()
    item = Database.fetchitem(id)
    data["youtube_id"] = item.youtube_id
    item.update(data)
        
@socketio.on('deleteitem')
def deleteitem(id):
    item = Database.fetchitem(id)
    try:
        os.unlink(item.filepath)
    except Exception:
        pass
    item.delete()
    sockets.overview({'msg': 'Item succesfully deleted!'})

@socketio.on('downloaditem')
def downloaditem(input):
    item = Database.fetchitem(input)
    if item is None:
        item = Database.checkfile(input)
        if item is None:
            sockets.overview({'msg': 'Filepath invalid'})
            return False
    path = item.filepath
    if os.path.exists(path) and os.path.isfile(path):
        if Database.checkfile(path) is not None:
            extension = path.split('.')[len(path.split('.')) - 1]
            filename = str(item.name) + "." + str(extension)
            mimetype = guess_type(path)
            with open(path, 'rb') as file:
                content = file.read()
            sockets.overview({'msg': 'download_file', 'data': content, 'filename': filename, 'mimetype': mimetype})
        else:
            sockets.overview({'msg': 'Filepath invalid'})
    else:
        sockets.overview({'msg': 'Filepath invalid'})
        
@socketio.on('fetchcover')
def fetchcover(id):
    item = Database.fetchitem(id)
    sockets.overview({'msg': 'load_cover', 'data': item.cover, 'id': id})
        
@socketio.on('editmetadata')
def editmetadata(id):
    item = Database.fetchitem(id)

    extension = item.filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
    if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
        metadata = MetaData.readaudiometadata(item.filepath)
    elif extension in ["M4A", 'MP4']:
        metadata = MetaData.readvideometadata(item.filepath)
    else:
        return False
    metadata["audio_id"] = item.audio_id
    metadata["itemid"] = item.id
    metadata["cover"] = item.cover
    metadata_sources = Config.get_metadata_sources()
    metadataform = render_template('metadataform.html', metadata_sources=metadata_sources)
    sockets.editmetadata({'metadata': metadata, 'metadataview': metadataform})

@socketio.on('editfile')
def editfile(id):
    item = Database.fetchitem(id)
    itemdata = {
        'filepath': item.filepath,
        'name': item.name,
        'album': item.album,
        'date': item.date,
        'length': item.length,
        'audio_id': item.audio_id,
        'youtube_id': item.youtube_id,
        'itemid': item.id
    }
    templates = Templates.fetchalltemplates()
    defaulttemplate = Templates.searchdefault()
    segment_results = sb.segments(itemdata["youtube_id"])
    segments = segment_results if type(segment_results) == list else 'error'
    downloadform = render_template('downloadform.html', templates=templates, segments=segments, default=defaulttemplate)
    sockets.editfile({'filedata': itemdata, 'downloadview': downloadform})
    
@socketio.on('editfilerequest')
def editfilerequest(filepath, id):
    item = Database.fetchitem(id)
    if item is not None:
        extension = item.filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
        new_extension = filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
        if item.cover != os.path.join(env.BASE_DIR, 'metatube/static/images/empty_cover.png'):
            try:
                response = requests.get(item.cover)
                image = response.content
                mime_type = guess_type(item.cover)
            except Exception:               
                sockets.downloadprogress({'status': 'error', 'message': 'Cover URL is invalid!'})
                return False
        else:
            file = open(item.cover, 'rb')
            image = file.read()
            mime_type = 'image/png'
        if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
            metadata_item = MetaData.readaudiometadata(item.filepath)
                        
        elif extension in ['MP4', 'M4A']:
            metadata_item = MetaData.readvideometadata(item.filepath)
            metadata_item["barcode"] = ""
            metadata_item["language"] = ""
            
        metadata_item["track_id"] = item.audio_id
        metadata_item["cover_path"] = item.cover
        metadata_item["cover_mime_type"]  = mime_type
        metadata_item["image"] = image
        metadata_item["itemid"] = item.id
        metadata_item["goal"] = 'edit'
        metadata_item["extension"] = new_extension
        metadata_item["filename"] = filepath
            
        if new_extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
            MetaData.mergeaudiodata(metadata_item)
        elif new_extension in ['MP4', 'M4A']:
            MetaData.mergevideodata(metadata_item)
        head, tail = os.path.split(filepath)
        move(filepath, os.path.join(head, tail[4:len(tail)]))
        try:
            os.unlink(item.filepath)
        except Exception:
            pass
        logger.info('Edited file %s', tail)
    else:
        logger.info('File not in database')
    
@socketio.on('editmetadatarequest')
def editmetadatarequest(metadata_user, filepath, id):
    extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
    data = MetaData.onlyuserdata(filepath, metadata_user)
    if data is not False:
        data["goal"] = 'edit'
        data["itemid"] = id
        data["extension"] = extension
        data["source"] = metadata_user["source"]
        if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
            MetaData.mergeaudiodata(data)
        elif extension in ['MP4', 'M4A']:
            MetaData.mergevideodata(data)
        elif extension in ['WAV']:
            MetaData.mergeid3data(data)
        else:
            return False

@bp.context_processor
def utility_processor():
    def path_exists(path):
        return os.path.exists(path)
    def get_ext(filepath):
        return filepath.split('.')[len(filepath.split('.')) - 1].upper()
    def check_metadata(filepath):
        return filepath.split('.')[len(filepath.split('.')) - 1].upper() in ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A']
    return dict(path_exists=path_exists, get_ext=get_ext, check_metadata=check_metadata)