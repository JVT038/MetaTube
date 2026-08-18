import json

from flask import render_template

from metatube import socketio
from metatube.database import Templates


@socketio.on("fetchtemplate")
def fetchtemplate(id):
    if id is not None and len(id) > 0:
        template = Templates.fetchtemplate(id)
        data = {
            "id": template.id,
            "name": template.name,
            "type": template.type,
            "extension": template.extension,
            "output_folder": template.output_folder,
            "output_name": template.output_name,
            "bitrate": template.bitrate,
            "resolution": template.resolution,
            "proxy_status": template.proxy_status,
            "proxy_type": template.proxy_type,
            "proxy_address": template.proxy_address,
            "proxy_port": template.proxy_port,
            "proxy_username": template.proxy_username,
            "proxy_password": template.proxy_password,
        }
        response = json.dumps(data)
        socketio.emit("template", response)
    else:
        socketio.emit("template", {"response": "Invalid ID"})


def error(e):
    return render_template("errors.html", e=e)
