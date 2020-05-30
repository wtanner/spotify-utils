import argparse
import os
import http.server
import socketserver
import webbrowser
import urllib.parse
import configparser

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

def webserver():
    """ spin up a simple web server """
    port = 8888
    Handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address=True

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("severing at port", port)
        httpd.serve_forever()

def main(**kwargs):
    config = configparser.ConfigParser()
    config ['SPOTIFYUTILS'] = {
        'ClIENT_ID': kwargs['client_id'],
        'CLIENT_SECRET': kwargs['client_secret'],
        'REDIRECT_URI': kwargs['redirect_uri'],
    }
    with open(kwargs['configfile'], "w") as f:
        config.write(f)

def authorize():
    """ Direct user to authorize spotify URL """
    requestUrl = "https://accounts.spotify.com/authorize"
    response_type = 'code'
    scope = 'user-read-email'
    show_dialog = 'true'

    PARAMS = {
        'client_id': kwargs['client_id'],
        'response_type': response_type,
        'redirect_uri': kwargs['redirect_uri'],
        'scope': scope,
        'show_dialog': show_dialog
    }

    authorizationURL = ('https://accounts.spotify.com/authorize?' + (urllib.parse.urlencode(PARAMS)))
    webbrowser.open_new(authorizationURL)