import argparse
import os
import configparser
import urllib.request
import urllib.parse
import base64
import json
from spotifyutils.config import configuration

#TODO: Add CLI capability, config_read, config_write, etc....

def cli(input_args=None):
    """Main playlist program entrypoint

    >>> cli(['config', '--client-id', 'asdf'])
    Test
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
        help='Spotify Client ID'
    )
    parser_config.add_argument(
        '--client-secret',
        type=str,
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
        help='Location on the filesystem to store configuration parameters'
    )

    # Playlist command
    playlist_config = subparsers.add_parser(
        'playlist', help='Utilities that deal with Spotify playlists'
    )

    args = parser.parse_args(input_args)
    configuration(**vars(args))
