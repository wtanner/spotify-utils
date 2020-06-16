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

def userAuth(redirect_uri, client_id):
    """ Generate and take user to Spotify Auth Page """

    global REDIRECT_URI 
    REDIRECT_URI = redirect_uri
    baseUrl = "https://accounts.spotify.com/authorize"
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

    authorizationURL = (baseUrl + "?" + (urllib.parse.urlencode(PARAMS)))
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

            self.path = 'spotifyutils/index.html'
            indexFile = open(self.path).read()
            self.send_response(200, 'OK')
            self.end_headers()
            self.wfile.write(bytes(indexFile, 'utf-8'))

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
    
    return AUTHCODE

def getTokens(client_id, client_secret):
    """Exchange auth code for access token"""

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