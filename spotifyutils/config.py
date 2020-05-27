import os

from getpass import getpass
from spotifyutils.auth import spotify_auth_uri, wait_for_auth_redirect, get_tokens


DEFAULTS = {
    'redirect_uri': 'https://localhost:8084/callback',
    'configfile': os.path.join(os.path.expanduser('~'), '.spotifyutils'),
}


def run(**kwargs):
    """Perform configuration, including initial authentication"""

    # TODO read from config file as well
    client_id = kwargs['client_id'] or input('Client ID: ')
    secret_id = kwargs['secret_id'] or getpass('Secret ID: ')
    redirect_uri = kwargs['redirect_uri'] or input(f'Redirect URI [{DEFAULTS["redirect_uri"]}]: ') or DEFAULTS['redirect_uri']
    configfile = kwargs['configfile'] or input(f'Configfile [{DEFAULTS["configfile"]}]: ') or DEFAULTS['configfile']

    # TODO find a better home for these
    scopes = ['playlist-read-private', 'playlist-modify-private']

    # Get an authorization code, access token and/or refresh token
    print('')
    print('TODO include instructions for setting up Spotify developer dashboard and project')

    print('')
    print('Browse to: ' + spotify_auth_uri(client_id, redirect_uri, scopes, '123'))

    print('')
    print('Note: This program generates a self-signed certificate for the redirect callback server. Your browser will likely prompt you before you can continue.')

    print('')
    print(f'Listening for redirect from Spotify at {redirect_uri}...')

    auth_code = wait_for_auth_redirect(redirect_uri)

    print('')
    print(f'Received an Authorization Code from Spotify for user {client_id}')

    print('')
    print('Requesting Access and Refresh tokens from Spotify...')

    access_token, refresh_token = get_tokens(code, client_id, client_secret, redirect_uri)

    print('')
    print('Got access and refresh tokens from Spotify')

    # TODO save everything to the config file

    print('')
    print(f'Configuration saved to {configfile}')

    print('')
    print('Configuration complete')
