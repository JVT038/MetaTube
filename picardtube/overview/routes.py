# from picardtube.ytdl import ytdlp
# from picardtube.mbp import MBP
# from picardtube.sponsorblock import sb
from picardtube.overview import bp
from picardtube.database import *
from picardtube.youtube import YouTube as yt
from math import floor
import picardtube.sponsorblock as sb
import picardtube.musicbrainz as musicbrainz
import os, json
from flask import render_template, request, jsonify

@bp.route('/')
def index():
    ffmpeg_path = True if len(Config.query.get(1).ffmpeg_directory) > 0 else False
    return render_template('overview.html', current_page='overview', ffmpeg_path=ffmpeg_path)

@bp.route('/ajax/search', methods=['GET'])
def search():
    query = request.args.get('query')
    amount = request.args.get('amount') if len(request.args.get('amount')) > 0 else 5
    if query is not None and len(query) > 1:
        if 0 < int(amount) < 100:
            try:
                video = yt.search(query)
                mbp = musicbrainz.search(
                    query = video["track"] if "track" in video else (video["alt_title"] if "alt_title" in video else video["title"]),
                    artist = video["artist"] if "artist" in video else (video["creator"] if "creator" in video else video["channel"]),
                    amount = amount
                )
                templates = Templates.query.all()
                segments = sb.segments(video["id"]) if type(sb.segments(video["id"])) == list else 'error'
                downloadform = render_template('downloadform.html', templates=templates, segments=segments)
                response = jsonify(status='success', yt=video, mbp=mbp["release-list"], downloadform=downloadform, segments=segments)
                return response
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