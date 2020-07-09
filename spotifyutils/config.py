import configparser
import getpass
import os
from spotifyutils.auth import user_auth, secure_server, server, get_tokens

#TODO: Write function that checks if access/refresh tokens exist. If so, don't go through flow. If not, go through flow. 
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
        client_id = kwargs['client_id'] or input('Client ID: ')
        client_secret = kwargs['client_secret'] or getpass.getpass(prompt='Client Secret: ')
        redirect_uri = kwargs['redirect_uri'] or input('Redirect URI: ')
        configfile = input('(optional) User Config File Location: ')
        
        if configfile:
            configfile = os.path.join(os.path.expanduser('~'), configfile)
        else:
            configfile = os.path.join(os.path.expanduser('~'), DEFAULT['configfile'])
            
        config['spotifyutils'] = {}
        config_params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'configfile': configfile
        }

        for key, value in config_params.items():
            config['spotifyutils'][key] = value  
            
        with open(configfile, "w") as write_config:
            config.write(write_config)
            

    print("Redirecting to Spotify Authorization URI, and spinning up web server")
    user_auth(redirect_uri, client_id)
    server()

    print("Getting Auth and Refresh Tokens")
    get_tokens(client_id, client_secret)