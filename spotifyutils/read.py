import urllib.request
import json


def get_playlists(access_token, spotify_id):
    """ This function lists all of the user's playlists """
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
        