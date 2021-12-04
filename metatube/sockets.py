from metatube import socketio

def downloadprogress(message):
    socketio.emit('downloadprogress', message)

def downloadsettings(message):
    socketio.emit('downloadsettings', message)
    
def changetemplate(message):
    socketio.emit('changetemplate', message)
    
def templatesettings(message):
    socketio.emit('templatesettings', message)
    
def searchvideo(message):
    socketio.emit('searchvideo', message)