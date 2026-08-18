import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError

from metatube import logger, sockets


class spotify_metadata:
    def __init__(self, id, secret):
        try:
            self.spotify = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    client_id=id, client_secret=secret
                )
            )
        except SpotifyOauthError as e:
            logger.error("Spotify authentication has failed. Error: %s", str(e))

    def search(self, data):
        searchresults = self.spotify.search(f"track:{data['title']}", data["max"])
        searchresults["query"] = data["title"]
        sockets.spotifysearch(searchresults)
        logger.info("Searched Spotify for track '%s' ", data["title"])

    def sockets_track(self, id):
        sockets.foundspotifytrack(self.spotify.track(id))

    def fetch_track(self, id):
        return self.spotify.track(id)

    def searchspotify(query, cred):
        spotify = spotify_metadata(cred[1], cred[0])
        spotify.search(query)
