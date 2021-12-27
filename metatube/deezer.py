import deezer
from metatube import sockets
class Deezer():
    def __init__(self):
        self.client = deezer.Client()
    
    def socketsearch(self, query, max):
        sockets.deezersearch(self.client.search(query, limit=max))
    
    def search(self, query, max):
        return self.client.search(query, limit=max)