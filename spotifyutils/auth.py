"""This module handles Spotify authentication.

Since these utilities, in general, require access to user private data, we are
required to follow the Authorization Code Flow. This flow requires additional
steps and complexity versus the simpler Application flow. See:
https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow

At a high level, the flow is implemented as follows:

1. In the Spotify developer dashboard
(https://developer.spotify.com/dashboard/applications), create a client ID.

2. Add a redirect URI as https://localhost:8084/callback

3. Generate a valid Spotify Auth URI using the client ID, redirect URI,
required OAuth scopes, and optionally a state to be used in verification (if
desired, but due to the short-lived nature of the redirect handler, it is low
risk to exclude).

4. Start the redirect handler HTTPS server, which creates a temporary
self-signed certificate.

5. Open the generated Spotify Auth URI in a web browser, and authenticate.

6. Once Spotify completes authentication, it will redirect to the provided
redirect URI /callback handler. The /callback handler parses the code out of
the query parameters, and returns the code to the user.

Usage:

>>> client_id = 'asdf'
>>> client_secret = 'asdf2'
>>> redirect_uri = 'https://localhost:8084/callback'
>>> scopes = ['read-playlist', 'write-playlist']
>>> state = '123'
>>> auth_uri = spotify_auth_uri(client_id, redirect_uri, scopes, state)
>>> code = wait_for_auth_redirect(redirect_uri)
>>> access_token, refresh_token = get_tokens(code, client_id, client_secret, redirect_uri)

"""
import base64
import http.server
import json
import ssl
import tempfile
import urllib.parse
import urllib.request

from spotifyutils.cert import generate_selfsigned_cert
from typing import List


# singletons/globals
_REDIRECT_URI = None
_AUTH_CODE = None


class _SpotifyAuthHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args, **kwargs):
        """Disable internal logging

        Logging is handled by BaseHTTPRequestHandler.log_message(). We replace
        this method with a noop. Otherwise, it pollutes stdout. Since we are
        not operating a proper production server, this logging is unnecessary
        for this application.

        See: https://stackoverflow.com/questions/20281709/how-do-you-override-basehttprequesthandler-log-message-method-to-log-to-a-file

        """

    def do_GET(self):
        """Handle Spotify authentication redirect"""
        global _AUTH_CODE
        global _REDIRECT_URI

        self.protocol_version = 'HTTP/1.1'

        # We will route the request based on endpoint, so parse it out of the
        # request.
        endpoint = urllib.parse.urlparse(self.path).path

        # If the request is to the token endpoint, we are expecting the auth
        # code to be in the query parameters, as set by the /callback endpoint.
        if endpoint == urllib.parse.urlparse(_REDIRECT_URI).path:
            params = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )
            _AUTH_CODE = params['code'][0]

            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            self.wfile.write('Close me!'.encode())

        # Default response for all other requests that aren't /callback
        else:
            self.send_response(404, 'NOT FOUND')


def secure_server(http_server, host):
    """Wrap the http server in a secure socket"""
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


def wait_for_auth_redirect(redirect_uri: str) -> str:
    """Run a temporary web server in order to wait for a Spotify auth redirect

    Blocks until Spotify returns from a redirect for authentication.
    """

    global _AUTH_CODE
    global _REDIRECT_URI

    if _AUTH_CODE:
        return _AUTH_CODE
    else:

        _REDIRECT_URI = redirect_uri

        # TODO wrap this in a ValueError exception when there is an invalid URI
        # format. Reraise as something like ValueError('Invalid URI Format').
        host, port = urllib.parse.urlparse(redirect_uri).netloc.split(':')

        # block waiting for a request
        with http.server.HTTPServer(
                (host, int(port)),
                _SpotifyAuthHTTPRequestHandler
        ) as server:
            server = secure_server(server, host)

            while not _AUTH_CODE:
                server.handle_request()

    return _AUTH_CODE


def spotify_auth_uri(
        client_id: str, redirect_uri: str, scopes: List[str], state: str=None
):
    """Build a request for the user to navigate to

    Usage:
    >>> cid = 'asdf'
    >>> redirect_uri = 'http://localhost'
    >>> scopes = ['read-playlist', 'write-playlist']
    >>> state = '123'
    >>> spotify_auth_uri(cid, redirect_uri, scopes, state)
    'https://accounts.spotify.com/authorize?client_id=asdf&scope=read-playlist+write-playlist&redirect_uri=http%3A%2F%2Flocalhost&state=123'
    """

    base_url = 'https://accounts.spotify.com/authorize' 
    query_params = urllib.parse.urlencode(
        {
            'client_id': client_id,
            'scope': ' '.join(scopes),
            'redirect_uri': redirect_uri,
            'state': state,
            'response_type': 'code',
        }
    )

    full_url = base_url + '?' + query_params

    return full_url


def get_tokens(
        auth_code,
        client_id,
        client_secret,
        redirect_uri,
        url: str='https://accounts.spotify.com/api/token/'
) -> dict:
    """Returns (access_token, refresh_token)"""
    # encode the data, if it exists
    encoded_data = urllib.parse.urlencode(
        {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
        }
    ).encode('ascii')

    headers = {
        'Authorization' : 'Basic ' + base64.standard_b64encode(
            f'{client_id}:{client_secret}'.encode()
        ).decode('ascii')
    }
    request = urllib.request.Request(url, encoded_data, headers)
    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read())

        return payload['access_token'], payload['refresh_token']
