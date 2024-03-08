import deezer
from metatube import sockets
class Deezer():
    @staticmethod
    def socketsearch(data: dict) -> None:
        client = deezer.Client()
        searchresults = client.search(data["title"], artist=data["artist"])
        list = []
        for result in searchresults:
            list.append(result.as_dict())
        maxlist = list[0:int(data["max"])]
        maxlist.append(data["title"])
        sockets.deezersearch(maxlist)
    
    @staticmethod
    def searchid(id: int) -> dict:
        client = deezer.Client()
        return client.get_track(id).as_dict()
    
    @staticmethod
    def sockets_track(id: int) -> None:
        client = deezer.Client()
        sockets.deezertrack(client.get_track(id).as_dict())