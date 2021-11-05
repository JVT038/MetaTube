from picardtube import app
from picardtube.ytdl import ytdlp
from flask import render_template_string, render_template, request, jsonify

@app.route('/')
def index():
    return render_template('overview.html', current_page='overview')

@app.route('/ajax/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query is not None:
        yt = ytdlp.search(query)
        response = jsonify(status='success', info=yt)
        return response
    if query is None:
        return "empty", 400