import shutil
from magic import Magic
from metatube.overview import bp
from metatube.database import *
from metatube.DatabaseExceptions import *
from metatube.youtube.manageDownloadProcess import manageDownloadProcess
from metatube.youtube.youtubeUtils import utils as ytutils
from metatube.youtube.downloadOptions import downloadOptions
from metatube.metadata.processMetadata import processMetadata
from metatube.deezer import Deezer
from metatube.spotify import spotify_metadata as Spotify
from metatube.genius import Genius
from metatube import socketio, sockets, Config as env
from flask import render_template, current_app
from datetime import datetime
from dateutil import parser
from distutils.util import strtobool
from shutil import move
from tempfile import mkdtemp
from zipfile import ZipFile
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
import json
import os
import requests
import random
import string

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.get_ffmpeg()) > 0 else False # type: ignore
    records = Database.getrecords()
    metadata_sources = Config.get_metadata_sources()
    metadataform = render_template('metadataform.html', metadata_sources=metadata_sources)
    genius = True if 'genius' in Config.get_metadata_sources().split(';') else False
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path, records=records, metadataview=metadataform, genius=genius)

@socketio.on('searchitem')
def handle_searchitem(query):
    items = Database.searchrecords(query)
    list = []
    for itemdata in items:
        item = {
            "name": itemdata.name,
            "artist": itemdata.artist,
            "album": itemdata.album,
            "date": itemdata.date,
            "filepath": itemdata.filepath,
            "youtube_id": itemdata.youtube_id,
            "id": itemdata.id,
            "image": itemdata.cover
        }
        list.append(item)
    sockets.searchitem(list)

@socketio.on('fetchallitems')
def searchitem():
    items = Database.getrecords()
    list = []
    for itemdata in items:
        item = {
            "name": itemdata.name,
            "artist": itemdata.artist,
            "album": itemdata.album,
            "date": itemdata.date,
            "filepath": itemdata.filepath,
            "youtube_id": itemdata.youtube_id,
            "id": itemdata.id,
            "image": itemdata.cover
        }
        list.append(item)
    sockets.searchitem(list)

@socketio.on('ytdl_search')
def search(query):
    if query is not None and len(query) > 1:
        if ytutils.is_supported(query):
            verbose = strtobool(str(env.LOGGER))
            video = ytutils.fetch_url(query, verbose)
            if Database.checkyt(video["id"]) is None: # type: ignore
                templates = Templates.fetchalltemplates()
                defaulttemplate = Templates.searchdefault()
                metadata_sources = Config.get_metadata_sources()
                socketio.start_background_task(ytutils.fetch_video, video, templates, metadata_sources, defaulttemplate)
            else:
                sockets.searchvideo('This video has already been downloaded!')
        else:
            socketio.start_background_task(ytutils.search, query)
    else:
        sockets.searchvideo('Enter an URL!')
        
        
@socketio.on('ytdl_template')
def filename(data):
    info_dict = json.loads(data["info_dict"])
    filename = ytutils.verifytemplate(data["template"], info_dict, False)
    sockets.filenametemplate(filename)

@socketio.on('searchmetadata')
def searchmetadata(data):
    sources = Config.get_metadata_sources()
    data["max"] = Config.get_max()
    if 'musicbrainz' in sources:
        socketio.start_background_task(musicbrainz.webui, data)
    if 'spotify' in sources:
        cred = Config.get_spotify().split(';')
        socketio.start_background_task(Spotify.searchspotify, data, cred)
    if 'deezer' in sources:
        socketio.start_background_task(Deezer.socketsearch, data)
    if 'genius' in sources and data["type"] == 'lyrics':
        token = Config.get_genius()
        socketio.start_background_task(Genius.searchsong, data, token)

@socketio.on('ytdl_download')
def download(data):
    ext = str(data["ext"]).upper() or 'MP3'
    item = None
    processedMetadata = None
    if data['goal'] == 'add':
        if Database.songidexists(data['userMetadata']['songid'] or -1) is True:
            sockets.downloadprocesserror("This song has already been downloaded.")
            return
        processedMetadata = processMetadata(data['userMetadata'], ext)
    elif data['goal'] == 'edit':
        item = Database.fetchitem(data['itemid'] or -1)
        if isinstance(item, Database) == False:
            return
        
    output_folder = data["output_folder"] or '/downloads'
    output_type = data["type"] or 'Audio'
    output_format = data["output_format"] or f'%(title)s.%(ext)s'
    bitrate = data["bitrate"] or 'best'
    skipfragments = json.loads(data["skipfragments"]) or {}
    proxy_data = json.loads(data["proxy_data"]) or {'proxy_type': 'None'}
    width = data["width"] or 'best'
    height = data["height"] or 'best'
    youtube_id = data['youtube_id']
    ffmpeg = Config.get_ffmpeg()
    hw_transcoding = Config.get_hwt()
    vaapi_device = hw_transcoding.split(';')[1] if 'vaapi' in hw_transcoding else ''
    verbose = True if str(env.LOGGER).lower() == 'true' else False
    
    ytdl_options = downloadOptions(
        youtube_id,
        ext,
        output_folder,
        output_type,
        output_format,
        bitrate,
        skipfragments,
        proxy_data,
        ffmpeg,
        hw_transcoding,
        vaapi_device,
        width,
        height,
        verbose
    )
    downloadProcess = manageDownloadProcess(ytdl_options, processedMetadata, data['goal'], item)
    socketio.start_background_task(downloadProcess.start_download, current_app._get_current_object()) # type: ignore
    logger.info('Request to download %s', data["youtube_id"])
    return 'OK'

@socketio.on('fetchmbprelease')
def fetchmbprelease(songid):
    logger.info('Request for musicbrainz release with id %s', songid)
    mbp = musicbrainz.search_id_release(songid)
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
    
@socketio.on('fetchgeniussong')
def fetchgeniussong(input_id):
    logger.info('Request for Genius song with id %s', input_id)
    token = Config.get_genius()
    genius = Genius(token)
    song = genius.fetchsong(input_id)
    sockets.foundgeniussong(song)

@socketio.on('fetchgeniusalbum')
def fetchgeniusalbum(input_id):
    logger.info('Request for Genius album with id %s', input_id)
    token = Config.get_genius()
    genius = Genius(token)
    genius.fetchalbum(input_id)
    
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
    try:
        item = Database.fetchitem(id)
        data["youtube_id"] = item.youtube_id
        item.update(data)
    except InvalidItemId:
        return
    
@socketio.on('downloaditems')
def downloaditems(items):
    tmpdir = mkdtemp()
    try:
        output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))
        zipfilename = "items_" + output_string + ".zip"
        zipfilepath = os.path.join(tmpdir, zipfilename)
        zipfile = ZipFile(zipfilepath, 'w')
        for item in items:
            filepath = Database.fetchitem(item).filepath
            filename = os.path.split(filepath)[1]
            if os.path.exists(filepath) and os.path.isfile(filepath):
                zipfile.write(filepath, filename)
        zipfile.close()
        file = open(zipfilepath, 'rb')
        content = file.read()
        file.close()
        magic = Magic(mime=True)
        mime = magic.from_file(zipfilepath)
        sockets.overview({'msg': 'download_file', 'data': content, 'filename': zipfilename, 'mimetype': mime})
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError as e:
            logger.error('An error occured whilst deleting the temporary file: %s', str(e))
        
@socketio.on('deleteitem')
def deleteitem(items):
    items = json.loads(items)
    for id in items:
        item = Database.fetchitem(id)
        try:
            os.unlink(item.filepath)
        except Exception:
            pass
        item.delete()
    socketdata = {'msg': 'Item succesfully deleted!'} if len(items) > 1 else {'msg': 'deleteitems'}
    sockets.overview(socketdata)
    return 'OK'

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
            magic = Magic(mime=True)
            mimetype = magic.from_file(path)
            with open(path, 'rb') as file:
                content = file.read()
            sockets.overview({'msg': 'download_file', 'data': content, 'filename': filename, 'mimetype': mimetype})
        else:
            sockets.overview({'msg': 'Filepath invalid'})
    else:
        sockets.overview({'msg': 'Filepath invalid'})
        
@socketio.on('playitem')
def playitem(input):
    item = Database.fetchitem(input)
    if item is None:
        item = Database.checkfile(input)
        if item is None:
            sockets.overview({'msg': 'Filepath invalid'})
            return False
    path = item.filepath
    if os.path.exists(path) and os.path.isfile(path):
        if Database.checkfile(path) is not None:
            magic = Magic(mime=True)
            mimetype = magic.from_file(path)
            with open(path, 'rb') as file:
                content = file.read()
            sockets.overview({'msg': 'play_file', 'data': content, 'itemdata': Database.itemtodict(item), 'mimetype': mimetype})
        else:
            sockets.overview({'msg': 'Filepath invalid'})
    else:
        sockets.overview({'msg': 'Filepath invalid'})
        
@socketio.on('showfilebrowser')
def showfilebrowser(visible, id, target_folder=None):
    default = Templates.searchdefault()
    if 'parent' in visible and target_folder is not None:
        folder = os.path.abspath(os.path.join(target_folder, os.pardir))
    elif target_folder is not None and os.path.isdir(target_folder) and os.path.exists(target_folder):
        folder = target_folder
    else:
        folder = default.output_folder
    contents = [x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))]
    contents.extend([x for x in os.listdir(folder) if not os.path.isdir(os.path.join(folder, x))])
    files = []
    for file in contents:
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            extension = path.split('.')[len(path.split('.')) - 1].upper()
            if extension not in env.AUDIO_EXTENSIONS and extension not in env.VIDEO_EXTENSIONS:
                continue
            if Database.checkfile(path) is not None:
                continue
            if 'files' not in visible:
                continue
        lastmodified = os.stat(path).st_mtime
        filesize = os.path.getsize(path)
        pathtype = 'file' if os.path.isfile(path) else 'directory'
        item = {
            'filepath': path,
            'filename': file,
            'lastmodified': lastmodified,
            'filesize': filesize,
            'pathtype': pathtype
        }
        files.append(item)
    sockets.overview({'msg': 'showfilebrowser', 'files': files, 'visible': visible, 'directory': folder, 'id': id})

@socketio.on('updatefile')
def updatefile(filepath, id):
    item = Database.fetchitem(id)
    item.updatefilepath(filepath)

@socketio.on('movefile')
def updatefile(directory, filename, id, overwrite=False):
    item = Database.fetchitem(id)
    old_filepath = item.filepath
    if os.path.exists(directory):
        extension = old_filepath.split('.')[len(old_filepath.split('.')) - 1].lower()
        if len(filename.split('.')) > 1 and filename.split('.')[len(filename.split('.')) - 1] == extension:
            new_filepath = os.path.join(directory, filename.strip())
        else:
            new_filepath = os.path.join(directory, filename.strip() + "." + extension)
        if os.path.exists(new_filepath) and overwrite is False:
            return 'File already exists'
        else:
            shutil.move(old_filepath, new_filepath)
            item.updatefilepath(new_filepath)
            
@socketio.on('createdirectory')
def createdirectory(currentdirectory, directoryname):
    if os.path.exists(currentdirectory):
        path = os.path.join(currentdirectory, directoryname)
        if os.path.exists(path) and os.path.isdir(path):
            response = {
                'msg': 'This directory already exists!',
                'status': 500
            }
            return response
        else:
            os.mkdir(path)
            response = {
                'msg': f'Created directory {path}',
                'filepath': path,
                'status': 200
            }
            logger.info('Created directory %s', path)
            return response
        
@socketio.on('removedirectory')
def removedirectory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        name = os.path.basename(directory)
        response = {
            'msg': 'Removed directory',
            'directory': name,
            'status': 200
        }
        logger.info('Removed directory %s', directory)
        return response
    else:
        response = {
            'msg': 'Directory does not exist!',
            'status': 500
        }
        return response
            
@socketio.on('editmetadata')
def editmetadata(id):
    item = Database.fetchitem(id)
    if item is None:
        return False
    extension = item.filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
    if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
        metadata = MetaData.readaudiometadata(item.filepath)
    elif extension in ["M4A", 'MP4']:
        metadata = MetaData.readVideoMetadata(item.filepath)
    else:
        return False
    metadata["songid"] = item.songid
    metadata["itemid"] = item.id
    metadata["cover"] = item.cover
    metadata_sources = Config.get_metadata_sources()
    metadataform = render_template('metadataform.html', metadata_sources=metadata_sources)
    sockets.editmetadata({'metadata': metadata, 'metadataview': metadataform})

@socketio.on('editfile')
def editfile(id):
    item = Database.fetchitem(id)
    if item is None:
        return False
    itemdata = {
        'filepath': item.filepath,
        'name': item.name,
        'album': item.album,
        'date': item.date,
        'length': item.length,
        'songid': item.songid,
        'youtube_id': item.youtube_id,
        'itemid': item.id
    }
    templates = Templates.fetchalltemplates()
    defaulttemplate = Templates.searchdefault()
    segment_results = sb.segments(itemdata["youtube_id"])
    segments = segment_results if type(segment_results) == list else 'error'
    downloadform = render_template('downloadform.html', templates=templates, segments=segments, default=defaulttemplate)
    sockets.editfile({'data': itemdata, 'downloadview': downloadform})
    
# @socketio.on('editfilerequest')
# def editfilerequest(filepath, id):
#     item = Database.fetchitem(id)
#     if item is not None:
#         extension = item.filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
#         new_extension = filepath.split('.')[len(item.filepath.split('.')) - 1].upper()
#         if item.cover != env.DEFAULT_COVER_PATH:
#             try:
#                 response = requests.get(item.cover)
#                 image = response.content
#                 magic = Magic(mime=True)
#                 mime_type = magic.from_buffer(image)
#             except Exception:               
#                 sockets.downloadprocesserror('Cover URL is invalid!')
#                 return False
#         else:
#             file = open(item.cover, 'rb')
#             image = file.read()
#             mime_type = 'image/png'
#         if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
#             metadata_item = MetaData.readaudiometadata(item.filepath)
                        
#         elif extension in ['MP4', 'M4A']:
#             metadata_item = MetaData.readVideoMetadata(item.filepath)
#             metadata_item["barcode"] = ""
#             metadata_item["language"] = ""
            
#         metadata_item["songid"] = item.songid
#         metadata_item["cover_path"] = item.cover
#         metadata_item["cover_mime_type"]  = mime_type
#         metadata_item["image"] = image
#         metadata_item["itemid"] = item.id
#         metadata_item["goal"] = 'edit'
#         metadata_item["extension"] = new_extension
#         metadata_item["filename"] = filepath
            
#         if new_extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
#             MetaData.mergeaudiodata(metadata_item)
#         elif new_extension in ['MP4', 'M4A']:
#             MetaData.mergevideodata(metadata_item)
#         head, tail = os.path.split(filepath)
#         move(filepath, os.path.join(head, tail[4:len(tail)]))
#         try:
#             os.unlink(item.filepath)
#         except Exception:
#             pass
#         logger.info('Edited file %s', tail)
#     else:
#         logger.info('File not in database')
    
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