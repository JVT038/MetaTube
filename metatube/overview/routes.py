from flask.templating import render_template_string
from metatube.overview import bp
from metatube.database import *

from metatube.youtube import YouTube as yt
from metatube import socketio, sockets
from flask import render_template, request, jsonify
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
from multiprocessing import Pool
from metatube.metadata import MetaData
import json

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path)

@socketio.on('ytdl_search')
def search(query):
    if query is not None and len(query) > 1:
        if yt.is_supported(query):
            video = yt.fetch_url(query)
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
            socketio.emit('mbp_response', mbp["release-list"])
            socketio.emit('ytdl_response', (video, downloadform))
        else:
            sockets.searchvideo('Enter a valid URL!')

    else:
        sockets.searchvideo('Enter an URL!')

@bp.route('/ajax/findcover', methods=['GET'])
def findcover():
    id = request.args.get('id')
    if id is not None:
        try:
            cover = musicbrainz.get_cover(id)
            response = jsonify(status='Success', cover=cover)
            return response
        except Exception as error:
            return str(error), 400
    if id is None:
        sockets.searchvideo('Submit a valid release ID!')

@bp.route('/downloadtemplate')
def template():
    templates = Templates.query.all()
    segments = sb.segments('https://www.youtube.com/watch?v=IcrbM1l_BoI')
    segments_data = segments if type(segments) == list else 'error'
    return render_template('downloadform.html', templates=templates, segments=segments_data)

@socketio.on('ytdl_download')
def download(url, ext='mp3', output_folder='downloads', type='Audio', output_format=f'%(title)s.%(ext)s', bitrate=192, skipfragments="{}", proxy_data={'proxy_status': False}, width=1920, height=1080):
    ffmpeg = Config.get_ffmpeg()
    hw_transcoding = Config.get_hwt()
    vaapi_device = hw_transcoding.split(';')[1] if 'vaapi' in hw_transcoding else ''
    print(vaapi_device)
    ytdl_options = yt.get_options(url, ext, output_folder, type, output_format, bitrate, skipfragments, proxy_data, ffmpeg, hw_transcoding, vaapi_device, width, height)
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