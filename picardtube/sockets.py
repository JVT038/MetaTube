from picardtube import socketio
from flask_socketio import emit, send
from musicbrainz import mergedata

def overview(message):
    socketio.emit('overview', message)

@socketio.on('merge')
def merge(release_id, filepath):
    pass