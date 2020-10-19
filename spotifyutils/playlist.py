import urllib.request
import json
from spotifyutils.config import read_config

def playlist(**kwargs):

    access_token, spotify_id = read_config()

    def read_playlist(access_token, spotify_id):

        endpoint = 'https://api.spotify.com/v1/me/playlists'
        headers = {
            'Authorization': 'Bearer ' + access_token
        }
        request = urllib.request.Request(endpoint, headers=headers)
        data = json.load(urllib.request.urlopen(request))['items']
        playlists = []
        for name in data:
            playlists.append(name['name'])
        print(playlists)
    
    if kwargs['read'] == True:
        read_playlist(access_token, spotify_id)
        