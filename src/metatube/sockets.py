from metatube import socketio


def downloadsettings(message):
    socketio.emit("downloadsettings", message)


def changetemplate(message):
    socketio.emit("changetemplate", message)


def templatesettings(message):
    socketio.emit("templatesettings", message)


def searchvideo(message):
    socketio.emit("searchvideo", message)


def overview(message):
    socketio.emit("overview", message)


def musicbrainzresults(data):
    socketio.emit("mbp_response", data)


def youtuberesults(data, downloadform, metadataform):
    socketio.emit("ytdl_response", (data, downloadform, metadataform))


def filenametemplate(data):
    socketio.emit("ytdl_template", data)


def editmetadata(data):
    socketio.emit("edit_metadata", data)


def editfile(data):
    socketio.emit("edit_file", data)


def metadatalog(msg):
    socketio.emit("metadatalog", msg)


def searchitem(data):
    socketio.emit("searchitem", data)


def youtubesearch(data):
    socketio.emit("youtubesearch", data)


def spotifysearch(data):
    socketio.emit("spotify_response", data)


def geniussearch(data):
    socketio.emit("genius_response", data)


def foundgeniussong(data):
    socketio.emit("genius_song", data)


def foundgeniusalbum(data):
    socketio.emit("genius_album", data)


def foundspotifytrack(data):
    socketio.emit("spotify_track", data)


def deezersearch(data):
    socketio.emit("deezer_response", data)


def deezertrack(data):
    socketio.emit("deezer_track", data)


def downloadprogress(downloaded_bytes, total_bytes):
    socketio.emit(
        "downloadprogress",
        {
            "status": "downloading",
            "downloaded_bytes": downloaded_bytes,
            "total_bytes": total_bytes,
        },
    )


def postprocessing(postprocessor):
    socketio.emit("postprocessing", {"postprocessor": postprocessor})


def finished_postprocessor(postprocessor, filepath):
    socketio.emit(
        "finished_postprocessor", {"postprocessor": postprocessor, "filepath": filepath}
    )


def finished_download():
    socketio.emit("finished_download")


def finished_metadata(response):
    socketio.emit(
        "finished_metadata", {"status": "finished_metadata", "data": response}
    )


def metadata_error(error):
    socketio.emit("downloaderror", {"status": "error", "message": error})


def downloaderrors(message):
    socketio.emit("downloaderror", message)
