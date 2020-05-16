# spotify-utils

This is a collection of programs that interact with Spotify.

## Utilities

### Playlists

```shell
spotifyplaylists --help

usage: spotifyplaylists [-h] --access-token ACCESS_TOKEN

Utilities that interact with Spotify playlists

optional arguments:
  -h, --help            show this help message and exit
  --access-token ACCESS_TOKEN
                        Spotify OAuth access token
```

## Installation from this repository

```shell
pip install .
```

## Design philosophy

These programs follow the [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy):

    1. Write programs that do one thing and do it well.
    2. Write programs to work together.
    3. Write programs to handle text streams, because that is a universal interface.
