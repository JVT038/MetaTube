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
    
def overview(message):
    socketio.emit('overview', message)
    
def musicbrainzresults(data):
    socketio.emit('mbp_response', data)
    
def youtuberesults(data, downloadform, metadataform):
    socketio.emit('ytdl_response', (data, downloadform, metadataform))
    
def editmetadata(data):
    socketio.emit('edit_metadata', data)

def editfile(data):
    socketio.emit('edit_file', data)

def metadatalog(msg):
    socketio.emit('metadatalog', msg)
    
def youtubesearch(data):
    socketio.emit('youtubesearch', data)