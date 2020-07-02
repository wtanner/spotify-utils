import http.server
import ssl
import urllib.parse
import urllib.request
import configparser
import webbrowser
import json
from spotifyutils.cert import generate_selfsigned_cert
import tempfile

REDIRECT_URI = None
AUTHCODE = None

def user_auth(redirect_uri: str, client_id: str):
    """ Generate Spotify auth link with PARAMS and open the link in the user's default web browser. """

    global REDIRECT_URI 
    REDIRECT_URI = redirect_uri
    base_url = "https://accounts.spotify.com/authorize"
    response_type = 'code'
    scope = 'user-read-email'
    show_dialog = 'true'

    PARAMS = {
        'client_id': client_id,
        'response_type': response_type,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'show_dialog': show_dialog
    }

    authorization_url = base_url + "?" + (urllib.parse.urlencode(PARAMS))
    webbrowser.open_new(authorization_url)

class WebServer(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """ Parse AUTHCODE sent to the redirect uri and direct user to index page if the get request path equals the redirect uri. """
        global AUTHCODE
        
        # Read URI from configfile
        uri = urllib.parse.urlparse(REDIRECT_URI).path

        # Parse path out of GET request
        endpoint = urllib.parse.urlparse(self.path).path

        if uri == endpoint:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            AUTHCODE = params['code'][0]

            self.path = 'spotifyutils/index.html'
            indexFile = open(self.path).read()
            self.send_response(200, 'OK')
            self.end_headers()
            self.wfile.write(bytes(indexFile, 'utf-8'))

        else:
            self.send_response(404, 'NOT FOUND')

def secure_server(http_server: str, host: int):
    """ Generate the SSL context required for a secure web server. """

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
        
def server() -> str:
    """ Spin up a web server based on information contained in the redirect uri and wrap in the SSL context generated in the secure_server function. 
    Listen for a get request from the spotify authorize endpoint as long as this program does not have an AUTHCODE. """
    
    host, port = urllib.parse.urlparse(REDIRECT_URI).netloc.split(':')

    if AUTHCODE:
        return AUTHCODE
    else:
        with http.server.HTTPServer((host, int(port)), WebServer) as httpd:
            httpd = secure_server(httpd, host)
            while not AUTHCODE:
                httpd.handle_request()
    
    return AUTHCODE

def get_tokens(client_id: str, client_secret: str) -> str:
    """ Exchange AUTHCODE for access and refresh tokens using the Spotify token endpoint and the redirect uri, client id, and client secret specified during configuration. Access and refresh tokens are returned. """

    tokenEndpoint = 'https://accounts.spotify.com/api/token'
    grant_type = 'authorization_code'
    
    encodedParams = urllib.parse.urlencode({
        'grant_type': grant_type,
        'code': AUTHCODE,
        'redirect_uri': REDIRECT_URI,
        'client_id': client_id,
        'client_secret': client_secret
    }).encode('ascii')

    request = urllib.request.Request(tokenEndpoint, encodedParams)
    response = urllib.request.urlopen(request).read()
    json_data = json.loads(response)
    return json_data['access_token'], json_data['refresh_token']