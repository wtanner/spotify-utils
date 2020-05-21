# spotify-utils

This is a collection of programs that interact with Spotify.

## Utilities

### Playlists

```shell
spotifyutils --help

usage: spotifyutils [-h] {config,playlist} ...

Utilities that interact with Spotify playlists

positional arguments:
  {config,playlist}  sub-command help
    config           Configure and authenticate
    playlist         Utilities that deal with Spotify playlists

optional arguments:
  -h, --help         show this help message and exit
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
