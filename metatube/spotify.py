import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from metatube import sockets, logger

class spotify_metadata():
    def __init__(self, id, secret):
        try:
            self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=id, client_secret=secret))
        except SpotifyOauthError as e:
            logger.error('Spotify authentication has failed. Error: %s', str(e))
            
    def get_item(self, data):
        searchresults = self.spotify.search(f"track:{data['title']}", data["max"])
        sockets.spotifysearch(searchresults)
        logger.info('Searched Spotify for track %s with artist %s', data["title"], data["artist"])
        
    def sockets_track(self, id):
        sockets.foundspotifytrack(self.spotify.track(id))
        
    def fetch_track(self, id):
        return self.spotify.track(id)