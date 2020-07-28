import configparser
import getpass
import os
from spotifyutils.auth import user_auth, secure_server, server, get_tokens, refresh_tokens, get_spotifyID

DEFAULT = {'configfile': '.spotifyutils.ini'}

def configuration(**kwargs: dict):
    """ If configfile arg is passed, check if any other args are passed. If additional args are passed, overwrite any existing args 
    specified in configfile. If additional arguments are NOT passed, simply read the values stored in the configfile. 
    If configfile is not passed, use the args passed in the CLI OR take user input. If the user chooses to entre a location for the configfile,
    a config file will be created. """

    config = configparser.ConfigParser()

    if kwargs['configfile']:
        configfile = kwargs['configfile']
        if kwargs['client_id'] or kwargs['client_secret'] or kwargs['redirect_uri']:
            client_id = kwargs['client_id']
            client_secret = kwargs['client_secret']
            redirect_uri = kwargs['redirect_uri']

            print("Redirecting to Spotify Authorization URI, and spinning up web server")
            user_auth(redirect_uri, client_id)
            server()

            print("Getting Auth and Refresh Tokens")
            ACCESS_TOKEN, REFRESH_TOKEN = get_tokens(client_id, client_secret)

            print("Getting Spotify ID")
            spotify_id = get_spotifyID(ACCESS_TOKEN)

        else:
            config.read(configfile)
            client_id = config.get('spotifyutils', 'client_id')
            client_secret = config.get('spotifyutils', 'client_secret')
            redirect_uri = config.get('spotifyutils', 'redirect_uri')
            spotify_id = config.get('user', 'spotify_id')
            if config.get('tokens', 'refresh_token'):
                REFRESH_TOKEN = config.get('tokens', 'refresh_token')
                ACCESS_TOKEN = refresh_tokens(client_id, client_secret, REFRESH_TOKEN)
            else:
                print("Redirecting to Spotify Authorization URI, and spinning up web server")
                user_auth(redirect_uri, client_id)
                server()

                print("Getting Auth and Refresh Tokens")
                ACCESS_TOKEN, REFRESH_TOKEN = get_tokens(client_id, client_secret)

                print("Getting Spotify ID")
                spotify_id = get_spotifyID(ACCESS_TOKEN)

    else:
        if os.path.exists(os.path.join(os.path.expanduser('~'), DEFAULT['configfile'])):
            configfile = os.path.join(os.path.expanduser('~'), DEFAULT['configfile'])
            
            config.read(configfile)
            client_id = config.get('spotifyutils', 'client_id')
            client_secret = config.get('spotifyutils', 'client_secret')
            redirect_uri = config.get('spotifyutils', 'redirect_uri')
            spotify_id = config.get('user', 'spotify_id')
            print("Reading from existing default configfile: ", client_id, client_secret, redirect_uri)

            if config.get('tokens', 'refresh_token'):
                REFRESH_TOKEN = config.get('tokens', 'refresh_token')
                ACCESS_TOKEN = refresh_tokens(client_id, client_secret, REFRESH_TOKEN)
            else:
                print("Redirecting to Spotify Authorization URI, and spinning up web server")
                user_auth(redirect_uri, client_id)
                server()

                print("Getting Auth and Refresh Tokens")
                ACCESS_TOKEN, REFRESH_TOKEN = get_tokens(client_id, client_secret)

                print("Getting Spotify ID")
                spotify_id = get_spotifyID(ACCESS_TOKEN)

        else:
            client_id = kwargs['client_id'] or input('Client ID: ')
            client_secret = kwargs['client_secret'] or getpass.getpass(prompt='Client Secret: ')
            redirect_uri = kwargs['redirect_uri'] or input('Redirect URI: ')
            configfile = input('(optional) User Config File Location: ')
        
            if configfile:
                configfile = os.path.join(os.path.expanduser('~'), configfile)
            else:
                configfile = os.path.join(os.path.expanduser('~'), DEFAULT['configfile'])

            print("Redirecting to Spotify Authorization URI, and spinning up web server")
            user_auth(redirect_uri, client_id)
            server()

            print("Getting Auth and Refresh Tokens")
            ACCESS_TOKEN, REFRESH_TOKEN = get_tokens(client_id, client_secret)

            print("Getting Spotify ID")
            spotify_id = get_spotifyID(ACCESS_TOKEN)

    def write_config(client_id, client_secret, redirect_uri, configfile, ACCESS_TOKEN, REFRESH_TOKEN, spotify_id):
        """ Write all values to configfile """
        
        config['spotifyutils'] = {}
        config['tokens'] = {}
        config['user'] = {}
        
        params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'configfile': configfile
        }

        tokens = {
            'access_token': ACCESS_TOKEN,
            'refresh_token': REFRESH_TOKEN
        }

        user = {
            'spotify_id': spotify_id
        }
        for key, value in params.items():
            config['spotifyutils'][key] = value
        
        for key, value in tokens.items():
            config['tokens'][key] = value

        for key, value in user.items():
            config['user'][key] = value
    
        with open(configfile, "w") as write_values:
            config.write(write_values)

    print("Writing to configfile")
    write_config(client_id, client_secret, redirect_uri, configfile, ACCESS_TOKEN, REFRESH_TOKEN, spotify_id)
    