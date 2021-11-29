from metatube import socketio

def downloadprogress(message):
    socketio.emit('downloadprogress', message)

def downloadsettings(message):
    socketio.emit('downloadsettings', message)