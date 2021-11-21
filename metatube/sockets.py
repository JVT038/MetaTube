from metatube import socketio

def overview(message):
    socketio.emit('overview', message)

@socketio.on('merge')
def merge(release_id, filepath, fragments):
    pass