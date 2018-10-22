
from __future__ import print_function
import base64
import requests
import os
import json
import time
import sys

from dotenv import load_dotenv
# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse

from spotipy.db import get_tokens_for_user, update_token_for_user

# Ensure secrets are loaded
load_dotenv()

# TODO document the auth flow that this code implements

class SpotifyOauthError(Exception):
    pass


class SpotifyClientCredentials(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, username):
        """
        username - id of user in data store
        token_info - Set on first call to get_access_token and updated on following calls when refresh is needed
        """
        self.username = username
        self.token_info = None

    def is_token_expired(self):
        now = int(time.time())

        # If default value (using for existing users)
        if(self.token_info['expires_at'] == 0):
            self.token_info['expires_at'] = 99999999999
        return int(self.token_info['expires_at']) < now

    def get_access_token(self):
        """
        Query DB for tokens, if token is expired, get refresh it and update DB.
        """
        self.token_info = get_tokens_for_user(self.username)

        if self.is_token_expired():
            print('UPDATING TOKEN')
            new_token_info = self.refresh_access_token(self.token_info['refresh_token'])

            print('token object returned from spotify api')
            print(new_token_info)

            success = update_token_for_user(self.username, new_token_info)
            print('update return value ' + str(success))

            self.token_info = new_token_info

        return self.token_info['access_token']

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info['expires_at'] = int(time.time()) + int(token_info['expires_in'])
        return token_info

    def refresh_access_token(self, refresh_token):
        payload = { 'refresh_token': refresh_token,
                   'grant_type': 'refresh_token'}

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers)
        if response.status_code != 200:
            if False:  # debugging code
                print('headers', headers)
                print('request', response.url)
            print("couldn't refresh token: code:%d reason:%s" \
                % (response.status_code, response.reason))
            return None
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if not 'refresh_token' in token_info:
            token_info['refresh_token'] = refresh_token
        return token_info

    def _make_authorization_headers(self):
        client_id = SpotifyClientCredentials.get_client_id()
        client_secret = SpotifyClientCredentials.get_client_secret()
        auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

    @staticmethod
    def get_client_id():
        return os.getenv('SPOTIFY_CLIENT_ID')

    @staticmethod
    def get_client_secret():
        return os.getenv('SPOTIFY_CLIENT_SECRET')
