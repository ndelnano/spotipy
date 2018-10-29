# Spotipy - a Python client for The Spotify Web API

## Description

Spotipy is a thin client library for the Spotify Web API.

## Differences in this fork!

Currently two things:

* Batching data to endpoints used in the playlist-maker. So far these endpoints include: checking saved tracks in user library, adding tracks to a user's playlist. There is likely more to come as that project progresses.
* Support for storing and updating user's access and refresh tokens in MySQL

To get jump started, do something like:

```
credentials = SpotifyClientCredentials(
    username, 
    db_creds=db.db.get_db_creds(),
    spotify_app_creds=get_spotify_app_creds()
)
spotify = spotipy.Spotify(client_credentials_manager=credentials)
```

What are the parameters to SpotifyClientCredentials? (also documented in spotipy/oauth2.py)
```
username - uniquely identifies user in MySQL table `users`, column `username`
    **the schema for this project is maintained in TODO fill this in here when I upload the schema
db_creds - dict of form:
    {
        'DB_HOST' : '',
        'DB_USER' : '',
        'DB_PASS' : '',
        'DB_NAME' : ''
    }
spotify_app_creds - dict of form:
    {
        'SPOTIFY_CLIENT_ID' : '',
        'SPOTIFY_CLIENT_SECRET : ''
    }
```

## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).


## Installation
If you already have [Python](http://www.python.org/) on your system you can install the library simply by downloading the distribution, unpack it and install in the usual fashion:

```bash
python setup.py install
```

You can also install it using a popular package manager with

```bash
pip install ndelnano_spotipy
```

or

```bash
easy_install ndelnano_spotipy
```


## Dependencies

- [Requests](https://github.com/kennethreitz/requests) - ndelnano_spotipy requires the requests package to be installed


## Quick Start
To get started, simply install spotipy, create a Spotify object and call methods:

```python
import spotipy
sp = spotipy.Spotify()

results = sp.search(q='weezer', limit=20)
for i, t in enumerate(results['tracks']['items']):
    print ' ', i, t['name']
```

A full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/ndelnano/spotipy/tree/master/examples).


## Reporting Issues

If you have suggestions, bugs or other issues specific to this library, file them [here](https://github.com/ndelnano/spotipy/issues). Or just send me a pull request.

## Version
TODO when official release is ready
