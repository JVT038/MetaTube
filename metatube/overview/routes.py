from flask.templating import render_template_string
from metatube.overview import bp
from metatube.database import *

from metatube.youtube import YouTube as yt
from metatube import socketio, metadata
from flask import render_template, request, jsonify
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
from multiprocessing import Pool
from metatube.metadata import MetaData
import os
import json

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path)

@socketio.on('ytdl_search')
def search(query):
    if query is not None and len(query) > 1:
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
        return "Enter an URL!", 400

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
        return "empty", 400

@bp.route('/downloadtemplate')
def template():
    templates = Templates.query.all()
    segments = sb.segments('https://www.youtube.com/watch?v=IcrbM1l_BoI')
    segments_data = segments if type(segments) == list else 'error'
    return render_template('downloadform.html', templates=templates, segments=segments_data)

@socketio.on('fetchtemplate')
def fetchtemplate(id):
    if id is not None and len(id) > 0:
        template = Templates.fetchtemplate(id)
        data = {
            "name": template.name,
            "type": template.type,
            "extension": template.extension,
            "output_folder": template.output_folder,
            "output_name": template.output_name,
            "bitrate": template.bitrate,
            'proxy_status': template.proxy_status,
            'proxy_type': template.proxy_type,
            'proxy_address': template.proxy_address,
            'proxy_port': template.proxy_port,
            'proxy_username': template.proxy_username,
            'proxy_password': template.proxy_password
        }
        response = json.dumps(data)
        socketio.emit('template', response)
    else:
        socketio.emit('template', {'response': 'Invalid ID'})

@socketio.on('ytdl_download')
def download(url, ext='mp3', output_folder='downloads', type='Audio', output_format=f'%(title)s.%(ext)s', bitrate=192, skipfragments="{}", proxy_data={'proxy_status': False}):
    proxy = json.loads(proxy_data)
    filepath = os.path.join(output_folder, output_format)
    ffmpeg = Config.get_ffmpeg()
    segments = json.loads(skipfragments)
    postprocessors = []
    format = 'bestaudio/best' if type == 'Audio' else 'bv+ba/b'
    # choose whether to use the FFmpegExtractAudio post processor or the FFmpegVideoConverter one
    if type == 'Audio':
        postprocessors.append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": ext,
            "preferredquality": bitrate
        })
    elif type == 'Video':
        postprocessors.append({
            "key": "FFmpegVideoConvertor",
            "preferedformat": ext
        })
    # If segments have been submitted by the user to exclude, add a ModifyChapters key and add ranges
    if len(segments) > 0:
        ranges = []
        for segment in segments:
            if len(segment["start"]) < 1 or len(segment["end"]) < 1:
                return jsonify('Fill all segment fields!'), 400
            else:
                ranges.append((int(segment["start"]), int(segment["end"])))
        postprocessors.append({
            'key': 'ModifyChapters',
            'remove_ranges': ranges
        })

    ytdl_options = {
        'format': format,
        'postprocessors': postprocessors,
        'ffmpeg_location': ffmpeg,
        'progress_hooks': [yt.download_hook],
        'outtmpl': filepath,
        'noplaylist': True
        # 'updatetime': True,
    }
    # Add proxy if proxy is enabled
    if proxy['proxy_status'] != 'None':
        proxy_string = proxy["proxy_status"].lower(
        ) + "://" + proxy["proxy_address"] + ":" + proxy["proxy_port"]
        if len(proxy["proxy_username"]) > 0:
            proxy_string += proxy_string + "@" + proxy["proxy_username"]
        if len(proxy["proxy_username"]) > 0:
            proxy_string += proxy_string + ":" + proxy["proxy_password"]
        ytdl_options["proxy"] = proxy_string
    
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
    elif extension in ['MP4', 'FLV', 'WEBM', 'MKV', 'AVI']:
        MetaData.mergevideodata(data)
    elif extension in ['WAV']:
        MetaData.mergeid3data(data)
    # if extension == 'MP3':
    #     MetaData.MP3(data)
    # elif extension == 'FLAC':
    #     MetaData.FLAC(data)