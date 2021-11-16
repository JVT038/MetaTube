# from metatube.ytdl import ytdlp
# from metatube.mbp import MBP
# from metatube.sponsorblock import sb
from flask.templating import render_template_string
from metatube.overview import bp
from metatube.database import *
from metatube.youtube import YouTube as yt
from metatube import socketio
from math import floor
import metatube.sponsorblock as sb
import metatube.musicbrainz as musicbrainz
import os, json
from queue import Queue
from flask import render_template, request, jsonify
from multiprocessing import Process, Pool
from itertools import product

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path)

@bp.route('/ajax/search', methods=['GET'])
@socketio.on('ytdl_search')
def search(query, amount = 5):
    if query is not None and len(query) > 1:
        if 0 < int(amount) < 100:

            try:              
                video = yt.search(query)
                mbp_args = {
                    'query': video["track"] if "track" in video else (video["alt_title"] if "alt_title" in video else video["title"]), 
                    'artist': video["artist"] if "artist" in video else (video["creator"] if "creator" in video else video["channel"]),
                    'amount': str(amount)
                }
                templates = Templates.query.all()
                
                pool = Pool(processes=2)
                mbp_results = pool.map_async(musicbrainz.search, [mbp_args])
                segments_results = pool.map_async(sb.segments, [video["id"]])
                
                segments = segments_results.get()[0] if type(segments_results.get()[0] == list) else 'error'
                mbp = mbp_results.get()[0]
                
                downloadform = render_template('downloadform.html', templates=templates, segments=segments)
                socketio.emit('mbp_response', mbp["release-list"])
                socketio.emit('ytdl_response', (video, downloadform))
                # response = jsonify(status='success', yt=video, mbp=mbp["release-list"], downloadform=downloadform)
                # return response
            
            except ValueError as error:
                return str(error), 400
            
        else:
            return "Enter a number below 100!", 400
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

@bp.route('/ajax/fetchtemplate')
def fetchtemplate():
    id = request.args.get('id')
    if id is not None and len(id) > 0:
        template = Templates.fetchtemplate(id)
        data = {
            "name": template.name,
            "type": template.type,
            "extension": template.extension,
            "output_folder": template.output_folder,
            "output_name": template.output_name,
            "bitrate": template.bitrate
        }
        response = jsonify(data)
        return response, 200
    else:
        response = jsonify('invalid ID')
        return response, 400
    
@bp.route('/ajax/downloadvideo', methods=['POST'])
def download():
    # declare all variables
    url = [request.form.get('url')]
    type = request.form.get('type', 'Audio')
    ext = request.form.get('ext', 'mp3')
    output_format = request.form.get('output_format', f'%(title)s.%(ext)s')
    bitrate = request.form.get('bitrate', 192)
    filepath = os.path.join(request.form.get('output_folder', 'downloads'), output_format)
    ffmpeg = Config.get_ffmpeg()
    segments = json.loads(request.form.get('segments', "{}"))
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
        'noplaylist': True,
        # 'updatetime': True, 
    }
    yt_instance = yt()
    yt_instance.get_video(url, ytdl_options)
    # Just a return function, otherwise Flask gets angry >:(
    return "downloading...", 200