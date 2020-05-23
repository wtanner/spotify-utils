import argparse
import os
import http.server
import socketserver
import webbrowser

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
        default='http://localhost:8082',
        help='Redirect URI (used for authentication)'
    )
    parser_config.add_argument(
        '--configfile',
        type=str,
        default=os.path.join(os.path.expanduser('~'), '.spotifyutils'),
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
        openWebPage()
        httpd.serve_forever()

def openWebPage():
    redirectURL = 'http://localhost:8888/spotifyutils'
    webbrowser.open_new(redirectURL)

def main(**kwargs):
    print(kwargs)
