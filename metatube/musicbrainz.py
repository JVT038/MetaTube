from flask import Request
import musicbrainzngs
from musicbrainzngs.musicbrainz import ResponseError
musicbrainzngs.set_useragent("metatube", "0.1", Request.base_url)
def search(args):
    query = args['query']
    artist = args['artist']
    limit = int(args['amount'])
    response = musicbrainzngs.search_releases(query, artist=artist, limit = limit)
    return response

def get_cover(releaseid):
    try:
        return musicbrainzngs.get_image_list(releaseid)
    except ResponseError as e:
        return e.message
    
    
def mergedata(filename, releaseid):
    pass