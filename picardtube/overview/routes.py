# from picardtube.ytdl import ytdlp
# from picardtube.mbp import MBP
# from picardtube.sponsorblock import sb
from picardtube.overview import bp
from picardtube.database import *
import picardtube.youtube as yt
import picardtube.sponsorblock as sb
import picardtube.musicbrainz as musicbrainz

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
                segments = sb.segments(video["id"]) if type(sb.segments(video["id"])) == 'list' else 'error'
                response = jsonify(status='success', yt=video, mbp=mbp["release-list"], segments=segments)
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
    return render_template('downloadform.html', templates=templates)