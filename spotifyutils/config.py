"""
Configuration command handler

If configfile arg is passed, check if any other args are passed. If
additional args are passed, overwrite any exisiting args in the configfile
and replace with passed args. The auth modules are then used to generate
access and refresh tokens. If additional args are NOT passed, read the
configfile and refresh access token if a refresh token exists. If a refresh
token DOES NOT exist, use auth modules to generate access and refresh
tokens. If no arg is passed with the config method, check if a configfile
exists in the default location. If a configfile DOES exist and a refresh
toekn DOES exist refresh the access token. If a configfile DOES exist and a
refresh token DOES NOT exist, use the auth modules to generate refresh and
access tokens. If a configfile DOES NOT exist in the default location,
create config params based on passed args or user input. Use the auth
modules to generate refresh and access tokens. Finally, write all config
params including refresh and access tokens to configfile.
"""
import configparser
import getpass
import os
import datetime
from spotifyutils.auth import user_auth, secure_server, server, get_tokens, \
    refresh_tokens
from typing import Tuple

DEFAULT_CONFIG_FILENAME = f"{os.path.join(os.path.expanduser('~'), '.spotifyutils.ini')}"

# define the configuration file format
CONFIG_FILE_FORMAT = {
    'main': {
        'client_id': None,
        'client_secret': None,
        'redirect_uri': None,
    },
    'tokens': {
        'access_token': None,
        'expires': None,
        'refresh_token': None
    },
}


def parse_config(**kwargs) -> Tuple[str, dict]:
    """
    >>> from pprint import pprint
    >>> pprint(parse_config(client_id='1234', client_secret='1234', configfile='fakefile'))
    ('fakefile',
     {'main': {'client_id': '1234', 'client_secret': '1234', 'redirect_uri': None},
      'tokens': {'access_token': None, 'refresh_token': None}})
    """
    # used to manage the configuration file
    config_parser = configparser.ConfigParser()

    # get the configuration filename if specified. Otherwise, use the default
    config_filename = kwargs.get('configfile') or DEFAULT_CONFIG_FILENAME

    # parse the file
    config_parser.read(config_filename)

    # combine the file with the user-provided options, preferring the user options if they exist
    config_dict = {
        section: {
            key: kwargs.get(key) or config_parser.get(section, key, fallback=None)
            for key in CONFIG_FILE_FORMAT[section]
        }
        for section in CONFIG_FILE_FORMAT.keys()
    }

    return config_filename, config_dict


def write_config(config_dict: dict, config_filename: str) -> None:
    """ Write all values to configfile """

    config_parser = configparser.ConfigParser()
    config_parser.read_dict(config_dict)

    with open(config_filename, 'w') as f:
        config_parser.write(f)


def token_expiration(expires_in: int):
    """This function computes the time at which the access token expires """
    now = datetime.datetime.utcnow()
    expires_at = now + datetime.timedelta(seconds=expires_in)
    return expires_at


def token_time_delta(token_expiration_date):
    """This function checks to see if the token has expired"""
    now = datetime.datetime.utcnow()
    expires_datetime_obj = datetime.datetime.strptime(token_expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    return now > expires_datetime_obj


def authorize_user(client_id: str, client_secret: str, redirect_uri: str) -> Tuple[str, int, str]:
    """ Take the user through the authorization flow with the values provided
    in the config file.
    """
    print("Redirecting to Spotify Authorization URI, and spinning up web server")
    user_auth(redirect_uri, client_id)

    print("Waiting for redirect from Spotify")
    server()

    print("Getting Auth, Refresh tokens and token lifespan")
    access_token, expires_in, refresh_token = get_tokens(client_id, client_secret)
    return access_token, expires_in, refresh_token


def configuration(**kwargs):
    print("\n")
    print("Entering configuration mode for spotify utilities")
    print("\n")
    print(
        (
            "Note: If you are changing to a different client_id or secret_id, you will "
            "need to manually remove the tokens from the configuration file "
            "if you would like to fetch them again."
        )
    )
    print("\n")

    config_filename, config_dict = parse_config(**kwargs)

    # Allow the user the opportunity to enter or confirm their client and redirect values
    config_dict['main'] = {
        k: input(f'Enter a {k} (or press enter to accept the default [{v}]): ') or v
        for k, v in config_dict['main'].items()
    }

    # None of the main values are allowed to be unspecified
    for key in config_dict['main']:
        assert config_dict['main'][key], f'{key} must be specified'

    # If there is no refresh token, we need to authorize
    if not config_dict['tokens'].get('refresh_token'):
        client_id = config_dict['main']['client_id']
        client_secret = config_dict['main']['client_secret']
        redirect_uri = config_dict['main']['redirect_uri']

        access_token, expires_in, refresh_token = authorize_user(client_id,
                                                                 client_secret,
                                                                 redirect_uri)

        expires_at = token_expiration(expires_in)

        config_dict['tokens']['access_token'] = access_token
        config_dict['tokens']['refresh_token'] = refresh_token
        config_dict['tokens']['expires'] = expires_at

        print("Writing configuration")
        write_config(config_dict, config_filename)

    # Check if the access_token has expired
    if config_dict['tokens'].get('access_token'):
        expires = config_dict['tokens'].get('expires')
        expired = token_time_delta(expires)
        if expired:
            client_id = config_dict['main'].get('client_id')
            client_secret = config_dict['main'].get('client_secret')
            refresh_token = config_dict['tokens'].get('refresh_token')

            access_token, expires_in = refresh_tokens(client_id, client_secret, refresh_token)
            expires_at = token_expiration(expires_in)

            config_dict['tokens']['access_token'] = access_token
            config_dict['tokens']['expires'] = expires_at

            print("Writing configuration")
            write_config(config_dict, config_filename)

    return config_dict['tokens'].get('access_token')
