from lyricsgenius import Genius as geniusobj
from metatube import logger, sockets
class Genius():
    def __init__(self, client_id):
        try:
            self.genius = geniusobj(client_id)
        except TypeError() as e:
            logger.error('Genius API failed: %s', str(e))
    
    def search(self, data):
        search =  self.genius.search_songs(data["title"], data["max"])
        sockets.geniussearch(search)
        logger.info('Searched Genius for track \'%s\' ', data["title"])
    
    def searchsong(data, token):
        genius = Genius(token)
        genius.search(data)
        
    def fetchsong(self, id):
        return self.genius.song(id)
    
    def fetchlyrics(self, url):
        return self.genius.lyrics(url)
        
    def fetchalbum(self, id):
        sockets.foundgeniusalbum(self.genius.album_tracks(id))