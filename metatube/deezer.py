import deezer
from metatube import sockets
class Deezer():
    @staticmethod
    def socketsearch(data: dict) -> None:
        with deezer.Client() as client:
            searchresults = client.search(data["title"], artist=data["artist"])
            list = []
            for result in searchresults:
                list.append(result.as_dict())
            maxlist = list[0:int(data["max"])]
            maxlist.append(data["title"])
            sockets.deezersearch(maxlist)
    
    @staticmethod
    def searchid(id: int) -> dict:
        with deezer.Client() as client:
            return client.get_track(id).as_dict()
    
    @staticmethod
    def sockets_track(id: int) -> None:
        with deezer.Client() as client:
            sockets.deezertrack(client.get_track(id).as_dict())