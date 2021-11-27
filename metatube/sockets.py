from metatube import socketio

def downloadprogress(message):
    socketio.emit('downloadprogress', message)