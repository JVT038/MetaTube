from flask.templating import render_template_string
from metatube.overview import bp
from metatube.database import *
from mimetypes import guess_type
from metatube.youtube import YouTube as yt
from metatube import socketio, sockets
from flask import render_template
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
from multiprocessing import Pool
from metatube.metadata import MetaData
import json
import os

@bp.route('/')
@bp.route('/index')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    records = Database.getrecords()
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path, records=records)

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

                pool = Pool()
                segments_results = pool.map_async(sb.segments, (video["id"], ))
                mbp_results = pool.map_async(musicbrainz.search, (mbp_args, ))

                segments = segments_results.get()[0] if type(segments_results.get()[0]) == list else 'error'
                mbp = mbp_results.get()[0]
                downloadform = render_template('downloadform.html', templates=templates, segments=segments)
                sockets.youtuberesults(video, downloadform)
                for release in mbp["release-list"]:
                    release["cover"] = musicbrainz.get_cover(release["id"])
                    sockets.musicbrainzresults(release)
            else:
                sockets.searchvideo('This video has already been downloaded!')
        else:
            sockets.searchvideo('Enter a valid URL!')

    else:
        sockets.searchvideo('Enter an URL!')

@socketio.on('ytdl_download')
def download(url, ext='mp3', output_folder='downloads', type='Audio', output_format=f'%(title)s.%(ext)s', bitrate=192, skipfragments="{}", proxy_data={'proxy_status': False}, width=1920, height=1080):
    ffmpeg = Config.get_ffmpeg()
    hw_transcoding = Config.get_hwt()
    vaapi_device = hw_transcoding.split(';')[1] if 'vaapi' in hw_transcoding else ''
    ytdl_options = yt.get_options(url, ext, output_folder, type, output_format, bitrate, skipfragments, proxy_data, ffmpeg, hw_transcoding, vaapi_device, width, height)
    if ytdl_options is not False:
        yt_instance = yt()
        yt_instance.get_video(url, ytdl_options)

@socketio.on('fetchmbprelease')
def fetchmbprelease(release_id):
    mbp = musicbrainz.search_id_release(release_id)
    socketio.emit('foundmbprelease', json.dumps(mbp))

@socketio.on('fetchmbpalbum')
def fetchmbpalbum(album_id):
    mbp = musicbrainz.search_id_release_group(album_id)
    socketio.emit('foundmbpalbum', json.dumps(mbp))

@socketio.on('mergedata')
def mergedata(filepath, release_id, metadata):
    metadata_user = metadata
    metadata_mbp = musicbrainz.search_id_release(release_id)
    cover_mbp = musicbrainz.get_cover(release_id)
    extension = filepath.split('.')[len(filepath.split('.')) - 1].upper()
    data = MetaData.getdata(filepath, metadata_user, metadata_mbp, cover_mbp)
    data["extension"] = extension
    if extension in ['MP3', 'OPUS', 'FLAC', 'OGG']:
        MetaData.mergeaudiodata(data)
    elif extension in ['MP4', 'M4A']:
        MetaData.mergevideodata(data)
    elif extension in ['WAV']:
        MetaData.mergeid3data(data)
        
@socketio.on('insertdata')
def inserttodb(data, ytid):
    data["ytid"] = ytid
    id = Database.insert(data)
    data["id"] = id
    sockets.overview({'msg': 'inserted_song', 'data': data})
        
@socketio.on('deleteitem')
def deleteitem(id):
    item = Database.fetchitem(id)
    try:
        os.unlink(item.filepath)
    except:
        pass
    item.delete()
    sockets.overview({'msg': 'Item succesfully deleted!'})
    
@socketio.on('edititem')
def edititem(data):
    pass

@socketio.on('downloaditem')
def downloaditem(input):
    item = Database.fetchitem(input)
    if item is None:
        item = Database.checkfile(input)
        if item is None:
            sockets.overview({'msg': 'Filepath invalid'})
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

@bp.context_processor
def utility_processor():
    def path_exists(path):
        return os.path.exists(path)
    return dict(path_exists=path_exists)