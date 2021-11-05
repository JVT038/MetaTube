from picardtube import app
from flask import Request
import musicbrainzngs
musicbrainzngs.set_useragent("PicardTube", "0.1", Request.base_url)
class MBP():
    
        
    def search(query, album = "", artist = ""):
        '''
        query = the query to look for
        album = any album to look for
        artist = name of an artist to look for
        '''
        return musicbrainzngs.search_releases(query, limit=5, artist=artist)
    
    def get_cover(releaseid):
        return musicbrainzngs.get_image_list(releaseid)