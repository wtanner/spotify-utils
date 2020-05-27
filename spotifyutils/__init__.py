import argparse
import os

import spotifyutils.config


def cli(input_args=None):
    """Main program entrypoint
    """
    parser = argparse.ArgumentParser(
        description='Utilities that interact with Spotify playlists'
    )

    subparsers = parser.add_subparsers(
        help='sub-command help',
        dest='command'
    )

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
        '--secret-id',
        type=str,
        default=os.getenv('SPOTIFY_SECRET_ID'),
        help='Spotify secret ID'
    )
    parser_config.add_argument(
        '--redirect-uri',
        type=str,
        help='Redirect URI (used for authentication)'
    )
    parser_config.add_argument(
        '--configfile',
        type=str,
        help='Location on the filesystem to store configuration parameters'
    )

    # Playlist command
    playlist_config = subparsers.add_parser(
        'playlist', help='Utilities that deal with Spotify playlists'
    )

    args = parser.parse_args(input_args)
    main(**vars(args))


def main(**kwargs):
    command = kwargs['command']

    if command == 'config':
        spotifyutils.config.run(**kwargs)
