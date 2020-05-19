import argparse
import os


def cli(input_args=None):
    """Main playlist program entrypoint

    >>> cli(['--access-token', 'asdf'])
    {'access_token': 'asdf'}
    """
    parser = argparse.ArgumentParser(
        description='Utilities that interact with Spotify playlists'
    )

    parser.add_argument(
        '--client-id',
        type=str,
        default=os.getenv('SPOTIFY_CLIENT_ID'),
        help='Spotify Client ID'
    )
    parser.add_argument(
        '--client-secret',
        type=str,
        default=os.getenv('SPOTIFY_CLIENT_SECRET'),
        help='Spotify client secret'
    )
    parser.add_argument(
        '--redirect-uri',
        type=str,
        default='http://localhost:8082',
        help='Redirect URI (used for authentication)'
    )

    args = parser.parse_args(input_args)
    main(**vars(args))


def main(**kwargs):
    print(kwargs)
