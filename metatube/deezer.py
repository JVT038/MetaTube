import deezer
from metatube import sockets
class Deezer():
       
    def socketsearch(data):
        with deezer.Client() as client:
            searchresults = client.search(data["title"], artist=data["artist"])
            list = []
            for result in searchresults:
                list.append(result.as_dict())
            maxlist = list[0:int(data["max"])]
            maxlist.append(data["title"])
            sockets.deezersearch(maxlist)
    
    def searchid(id):
        with deezer.Client() as client:
            return client.get_track(id).as_dict()
    
    def sockets_track(id):
        with deezer.Client() as client:
            sockets.deezertrack(client.get_track(id).as_dict())