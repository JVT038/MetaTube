import sponsorblock
from sponsorblock.errors import *
from metatube.database import Templates
from metatube import socketio
from flask import render_template
def segments(url):
    client = sponsorblock.Client()
    try:
        segments = client.get_skip_segments(url)
        response = []
        for segment in segments:
            response.append(segment.data)
        print('Done with segments \n')
        return response
    
    except Exception as e:
        print(str(e))
        return str(e)