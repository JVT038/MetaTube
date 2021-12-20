from metatube.overview import bp
from metatube.database import *
from mimetypes import guess_type
from metatube.youtube import YouTube as yt
from metatube.metadata import MetaData
from metatube import socketio, sockets
from metatube import Config as env
from flask import render_template
from datetime import datetime
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
import json
import os
import asyncio

@bp.route('/')
@bp.route('/index')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    records = Database.getrecords()
    metadataform = render_template('metadataform.html')
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path, records=records, metadataview=metadataform)

@socketio.on('ytdl_search')
def search(query):
    if query is not None and len(query) > 1:
        if yt.is_supported(query):
            video = yt.fetch_url(query)
            if Database.checkyt(video["id"]) is None:
                templates = Templates.fetchalltemplates()
                mbp_args = {
                    'query': video["track"] if "track" in video else (video["alt_title"] if "alt_title" in video else video["title"]),
                    'artist': video["artist"] if "artist" in video else (video["creator"] if "creator" in video else video["channel"]),
                    'max': Config.get_max(),
                    'type': 'webui'
                }

                segments_search = asyncio.run(sb.segments(video["id"]))
                mbp = asyncio.run(musicbrainz.search(mbp_args))
                segments = segments_search if type(segments_search) == list else 'error'
                
                downloadform = render_template('downloadform.html', templates=templates, segments=segments)
                metadataform = render_template('metadataform.html')
                
                sockets.youtuberesults(video, downloadform, metadataform)
                if len(mbp["release-list"]) > 0:
                    for release in mbp["release-list"]:
                        release["cover"] = musicbrainz.get_cover(release["id"])
                    socketio.start_background_task(sockets.musicbrainzresults, mbp["release-list"])
                    logger.info('Sent musicbrainz release')
                else:
                    sockets.searchvideo('No releases from Musicbrainz have been found!')
            else:
                sockets.searchvideo('This video has already been downloaded!')
        else:
            asyncio.run(yt.search(query))
    else:
        sockets.searchvideo('Enter an URL!')

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
    verbose = bool(env.LOGGER)
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

@socketio.on('mergedata')
def mergedata(filepath, release_id, metadata):
    if Database.checkmusicbrainz(release_id) is None:
        metadata_user = metadata
        metadata_mbp = musicbrainz.search_id_release(release_id)
        cover_mbp = musicbrainz.get_cover(release_id)
        extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
        data = MetaData.getdata(filepath, metadata_user, metadata_mbp, cover_mbp)
        data["goal"] = 'add'
        if data is not False:
            data["extension"] = extension
            if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
                MetaData.mergeaudiodata(data)
            elif extension in ['MP4', 'M4A']:
                MetaData.mergevideodata(data)
            elif extension in ['WAV']:
                MetaData.mergeid3data(data)
            else:
                file = open(os.path.join(env.BASE_DIR, 'metatube/static/images/empty_cover.png'), 'rb')
                image = file.read()
                # The name will be the filename of the downloaded file without the extension
                name = filepath[0:len(filepath) - len(filepath.split('.')[len(filepath.split('.')) - 1]) - 1]
                data = {
                    'filepath': os.path.join(env.BASE_DIR, data["filename"]),
                    'name': name,
                    'artist': 'Unknown',
                    'album': 'Unknown',
                    'date': datetime.now(),
                    'length': 'Unknown',
                    'image': image,
                    'musicbrainz_id': 'Unknown'
                }
                sockets.downloadprogress({'status': 'metadata_unavailable', 'data': data})
                logger.debug('Metadata unavailable for file %s', data["filepath"])
    else:
        sockets.searchvideo('Musicbrainz release has already been downloaded!')
        try:
            os.unlink(filepath)
        except Exception:
            pass
        
@socketio.on('insertitem')
def insertitem(data):
    logger.info('Got request to insert data')
    id = Database.insert(data)
    data["id"] = id
    sockets.overview({'msg': 'inserted_song', 'data': data})
    
@socketio.on('updateitem')
def updateitem(data):
    logger.info('Got request to update item')
    id = data["itemid"]
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
    metadata["musicbrainz_id"] = item.musicbrainz_id
    metadata["itemid"] = item.id
    
    metadataform = render_template('metadataform.html')
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
        'musicbrainz_id': item.musicbrainz_id,
        'youtube_id': item.youtube_id
    }
    templates = Templates.fetchalltemplates()
    segment_results = asyncio.run(sb.segments(itemdata["youtube_id"]))
    segments = segment_results if type(segment_results) == list else 'error'
    downloadform = render_template('downloadform.html', templates=templates, segments=segments)
    sockets.editfile({'filedata': itemdata, 'downloadview': downloadform})
    
@socketio.on('editmetadatarequest')
def editmetadatarequest(metadata_user, release_id, filepath, id):
    metadata_mbp = musicbrainz.search_id_release(release_id)
    cover_mbp = musicbrainz.get_cover(release_id)
    extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
    data = MetaData.getdata(filepath, metadata_user, metadata_mbp, cover_mbp)
    data["goal"] = 'edit'
    data["itemid"] = id
    if data is not False:
        data["extension"] = extension
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
        return filepath.split('.')[len(filepath.split('.')) - 1].upper() in ['MP3', 'OPUS', 'FLAC', 'OGG', 'MP4', 'M4A', 'WAV']
    return dict(path_exists=path_exists, get_ext=get_ext, check_metadata=check_metadata)