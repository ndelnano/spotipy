from setuptools import setup

setup(
    name='ndelnano_spotipy',
    version='0.0.4',
    description='simple client for the Spotify Web API, adding mysql for token storage/access',
    author="@ndelnano",
    author_email="nickdelnano@gmail.com",
    url='http://spotipy.readthedocs.org/',
    install_requires=[
        'requests>=2.3.0',
        'six>=1.10.0',
        'mysqlclient'
    ],
    license='LICENSE.txt',
    packages=['spotipy'])
