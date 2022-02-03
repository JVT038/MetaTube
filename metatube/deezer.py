import deezer
from metatube import sockets
class Deezer():
       
    def socketsearch(data):
        client = deezer.Client()
        searchresults = client.search(data["title"], artist=data["artist"])
        list = []
        for result in searchresults:
            list.append(result.as_dict())
        maxlist = list[0:int(data["max"])]
        sockets.deezersearch(maxlist)
    
    def searchid(id):
        client = deezer.Client()
        return client.get_track(id).as_dict()
    
    def sockets_track(id):
        client = deezer.Client()
        sockets.deezertrack(client.get_track(id).as_dict())