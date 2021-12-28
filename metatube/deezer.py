import deezer
from metatube import sockets
class Deezer():
       
    def socketsearch(data):
        client = deezer.Client()
        searchresults = client.search(data["title"], limit=data["max"], artist=data["artist"])
        list = []
        for result in searchresults:
            list.append(result.as_dict())
        sockets.deezersearch(list)
    
    def searchid(id):
        client = deezer.Client()
        return client.get_track(id).as_dict()
    
    def sockets_track(id):
        client = deezer.Client()
        sockets.deezertrack(client.get_track(id).as_dict())