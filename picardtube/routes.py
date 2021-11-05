from picardtube import app
from picardtube.ytdl import ytdlp
from picardtube.mbp import MBP
from flask import render_template_string, render_template, request, jsonify

@app.route('/')
def index():
    return render_template('overview.html', current_page='overview')

@app.route('/ajax/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query is not None:
        video = ytdlp.search(query)
        mbp = MBP.search(
            query = video["track"] if "track" in video else (video["alt_title"] if "alt_title" in video else video["title"]),
            artist = video["artist"] if "artist" in video else (video["creator"] if "creator" in video else video["channel"])
        )
        response = jsonify(status='success', yt=video, mbp=mbp["release-list"])
        return response
    if query is None:
        return "empty", 400

@app.route('/ajax/findcover', methods=['GET'])
def findcover():
    id = request.args.get('id')
    if id is not None:
        cover = MBP.get_cover(id)
        response = jsonify(status='Success', cover=cover)
        return response
    if id is None:
        return "empty", 400