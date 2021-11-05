from picardtube import app
from flask import Request
import musicbrainzngs
musicbrainzngs.set_useragent("PicardTube", "0.1", Request.base_url)
class MBP():
    
        
    def search(value, type = None, album = "", artist = ""):
        return musicbrainzngs.search_releases(value, limit=1, artist=artist)
        