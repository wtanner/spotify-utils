import argparse
import os
import configparser
from spotifyutils.auth import userAuth, server, getTokens

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
        default='https://localhost:8084/spotifyutils/',
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

    client_id = parser.get('spotifyutils', 'client_id')
    client_secret = parser.get('spotifyutils', 'client_secret')
    redirect_uri = parser.get('spotifyutils', 'redirect_uri')

    print("Redirecting to Spotify Authorization URI, and spinning up web server")
    userAuth(redirect_uri, client_id)
    server()

    print("Getting Auth and Refresh Tokens")
    getTokens(client_id, client_secret)
