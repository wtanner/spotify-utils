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
        '--access-token',
        type=str,
        required=True,
        help='Spotify OAuth access token'
    )

    args = parser.parse_args(input_args)
    main(**vars(args))


def main(**kwargs):
    print(kwargs)
