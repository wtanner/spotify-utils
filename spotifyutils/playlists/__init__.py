import argparse
import os


def cli():
    parser = argparse.ArgumentParser(
        description='Utilities that interact with Spotify playlists'
    )

    parser.add_argument(
        '--access-token',
        type=str,
        required=True,
        help='Spotify OAuth access token'
    )

    args = parser.parse_args()
    main(**vars(args))


def main(**kwargs):
    print(kwargs)
