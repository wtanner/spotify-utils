import argparse
import os
import http.server
import socketserver
import webbrowser
import urllib.parse
import configparser
import tempfile
import base64
import ssl
from spotifyutils.cert import generate_selfsigned_cert

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
        default='https://localhost:8888/spotifyutils/',
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
            print('made it to do_get')
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            AUTHCODE = params['code'][0]

            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write('Close me!'.encode())

        else:
            self.send_response(404, 'NOT FOUND')

def secureServer(http_server, host):
    """ generate items required to make web server secure """

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # create a temporary, throwaway certificate
    cert, private = generate_selfsigned_cert(host)

    # these files are deleted after the context exists
    with tempfile.NamedTemporaryFile() as cert_file:
        with tempfile.NamedTemporaryFile() as key_file:

            cert_file.write(cert)
            key_file.write(private)
            cert_file.flush()
            key_file.flush()

            ssl_context.load_cert_chain(
                cert_file.name, key_file.name
            )

    http_server.socket = ssl_context.wrap_socket(http_server.socket, server_side=True)    
    return http_server
        
def server():
    """ create a web server to handle the get request """
    
    host, port = urllib.parse.urlparse(REDIRECT_URI).netloc.split(':')

    if AUTHCODE:
        return AUTHCODE
    else:
        with http.server.HTTPServer((host, int(port)), WebServer) as httpd:
            httpd = secureServer(httpd, host)
            while not AUTHCODE:
                httpd.handle_request()


#RequestAccessToken()
def RequestAccessToken():
    """Exchange auth code for access token"""
    parser = configparser.ConfigParser()
    parser.read(configfile)

    tokenEndpoint = 'https://accounts.spotify.com/api/token'
    grant_type = 'authorization_code'
    b64client_id = base64.standard_b64encode(parser.get('spotifyutils', 'client_id'))
    b64client_secret = base64.standard_b64encode(parser.get('spotifyutils', 'client_secret'))
    
    urlEncodedParams = urllib.parse.urlencode({
        'grant_type': grant_type,
        'code': AUTHCODE,
        'redirect_uri': REDIRECT_URI
    })

    Header = {
        'Authorization': 'Basic',
        b64client_id: b64client_secret
    }
    print("this is the header: ", Header)