from distutils.core import setup

setup(
    name='Spotify Utilities',
    version='0.1',
    packages=[
        'spotifyutils', 'spotifyutils.playlists'
    ],
    entry_points={
        'console_scripts': [
            'spotifyutils = spotifyutils:cli'
        ]
    }
)
