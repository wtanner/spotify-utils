import argparse
import os
import configparser
from spotifyutils.auth import user_auth, server, get_tokens

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
    """ Interpret passed arguments and execute the program """
    
    # if configfile arg is passed, check if any other args are passed. If additional args are passed, overwrite any existing args 
    # specified in configfile. If additional arguments are NOT passed, simply read the values stored in the configfile. 
    # If configfile is not passed, just use CLI args passed.

    if kwargs['configfile']:
        configfile = kwargs['configfile']
        config = configparser.ConfigParser()
        if kwargs['client_id'] or kwargs['client_secret'] or kwargs['redirect_uri']:
            config['spotifyutils'] = {}

            for key, value in kwargs.items():
                config['spotifyutils'][key] = value

            with open(configfile, "w") as write_config:
                config.write(write_config)
            
            client_id = kwargs['client_id']
            client_secret = kwargs['client_secret']
            redirect_uri = kwargs['redirect_uri']
        else:
            config.read(configfile)
            client_id = config.get('spotifyutils', 'client_id')
            client_secret = config.get('spotifyutils', 'client_secret')
            redirect_uri = config.get('spotifyutils', 'redirect_uri')
    else:
        client_id = kwargs['client_id']
        client_secret = kwargs['client_secret']
        redirect_uri = kwargs['redirect_uri']


    print("Redirecting to Spotify Authorization URI, and spinning up web server")
    user_auth(redirect_uri, client_id)
    server()

    print("Getting Auth and Refresh Tokens")
    accessToken, refreshToken = get_tokens(client_id, client_secret)