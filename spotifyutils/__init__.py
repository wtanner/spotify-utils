import argparse
import os
import http.server
import socketserver
import webbrowser
import urllib.parse
import configparser

configfile = ''
REDIRECT_URI = ''
AUTHCODE = ''

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

    global REDIRECT_URI
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
    REDIRECT_URI = parser.get('spotifyutils', 'redirect_uri')
    baseUrl = "https://accounts.spotify.com/authorize?"
    response_type = 'code'
    scope = 'user-read-email'
    show_dialog = 'true'

    PARAMS = {
        'client_id': parser.get('spotifyutils', 'client_id'),
        'response_type': response_type,
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'show_dialog': show_dialog
    }

    authorizationURL = (baseUrl + (urllib.parse.urlencode(PARAMS)))
    webbrowser.open_new(authorizationURL)


class WebServer(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """ Handle auth code sent to redirect URI """
        global AUTHCODE
        
        # Read URI from configfile
        uri = urllib.parse.urlparse(REDIRECT_URI).path

        # Parse path out of GET request
        endpoint = urllib.parse.urlparse(self.path).path

        if uri == endpoint:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            AUTHCODE = params['code'][0]

            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write('Close me!'.encode())

        else:
            self.send_response(404, 'NOT FOUND')
        
def server():
    """ create a web server to handle the get request """

    host, port = urllib.parse.urlparse(REDIRECT_URI).netloc.split(':')
    socketserver.TCPServer.allow_reuse_address=True

    if AUTHCODE == '':
        with socketserver.TCPServer((host, int(port)), WebServer) as httpd:
            print("severing at port", port)
            while not AUTHCODE:
                print("This is the authcode in the server, if authcode loop:, ", AUTHCODE)
                httpd.handle_request()       