import argparse
import os
import http.server
import socketserver
import webbrowser
import urllib.parse
import configparser

configfile = ''

def cli(input_args=None):
    """Main playlist program entrypoint

    >>> cli(['config', '--client-id', 'asdf'])
    Test
    """
    parser = argparse.ArgumentParser(
        description='Utilities that interact with Spotify playlists'
    )

    subparsers = parser.add_subparsers(help='sub-command help')

    # Configuration command
    parser_config = subparsers.add_parser(
        'config', help='Configure and authenticate'
    )
    parser_config.add_argument(
        '--client-id',
        type=str,
        default=os.getenv('SPOTIFY_CLIENT_ID'),
        help='Spotify Client ID'
    )
    parser_config.add_argument(
        '--client-secret',
        type=str,
        default=os.getenv('SPOTIFY_CLIENT_SECRET'),
        help='Spotify client secret'
    )
    parser_config.add_argument(
        '--redirect-uri',
        type=str,
        default='http://localhost:8888/spotifyutils/',
        help='Redirect URI (used for authentication)'
    )
    parser_config.add_argument(
        '--configfile',
        type=str,
        default=os.path.join(os.path.expanduser('~'), '.spotifyutils.ini'),
        help='Location on the filesystem to store configuration parameters'
    )

    # Playlist command
    playlist_config = subparsers.add_parser(
        'playlist', help='Utilities that deal with Spotify playlists'
    )

    args = parser.parse_args(input_args)
    main(**vars(args))

def main(**kwargs):
    """ Direct user to authorize spotify URL """

    global configfile
    configfile = kwargs['configfile']
    
    config = configparser.ConfigParser()
    config ['spotifyutils'] = {
        'ClIENT_ID': kwargs['client_id'],
        'CLIENT_SECRET': kwargs['client_secret'],
        'REDIRECT_URI': kwargs['redirect_uri']
    }

    with open(configfile, "w") as f:
        config.write(f)

    parser = configparser.ConfigParser()
    parser.read(configfile)
    baseUrl = "https://accounts.spotify.com/authorize?"
    response_type = 'code'
    scope = 'user-read-email'
    show_dialog = 'true'

    PARAMS = {
        'client_id': parser.get('spotifyutils', 'client_id'),
        'response_type': response_type,
        'redirect_uri': parser.get('spotifyutils', 'redirect_uri'),
        'scope': scope,
        'show_dialog': show_dialog
    }

    authorizationURL = (baseUrl + (urllib.parse.urlencode(PARAMS)))
    webbrowser.open_new(authorizationURL)


class WebServer(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """ Handle auth code sent to redirect URI """
        print("configfile in the doGET function: ", configfile)
        selfPath = self.path
        endpoint = urllib.parse.urlparse(self.path).path
        

        
def server():
    """ create a web server to handle the get request """
    port = 8888
    socketserver.TCPServer.allow_reuse_address=True

    with socketserver.TCPServer(("", port), WebServer) as httpd:
        print("severing at port", port)
        httpd.serve_forever()               