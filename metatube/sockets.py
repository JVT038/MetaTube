from metatube import socketio
from flask_socketio import emit, send
from metatube.musicbrainz import mergedata
from metatube.ffmpeg import ffmpeg
from metatube import Config
from json import loads
from threading import Thread
import os

def overview(message):
    socketio.emit('overview', message)

@socketio.on('merge')
def merge(release_id, filepath, fragments):
    pass