from picardtube import socketio
from flask_socketio import emit, send
from picardtube.musicbrainz import mergedata
from picardtube.ffmpeg import ffmpeg
from picardtube import Config
from json import loads
from threading import Thread
import os

def overview(message):
    socketio.emit('overview', message)

@socketio.on('merge')
def merge(release_id, filepath, fragments):
    pass