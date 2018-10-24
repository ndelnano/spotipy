
from __future__ import print_function
import base64
import requests
import os
import json
import time
import sys

# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse

import MySQLdb

# TODO document the auth flow that this code implements

class SpotifyOauthError(Exception):
    pass


class SpotifyClientCredentials(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, username, db_creds, spotify_app_creds):
        """
        username - id of user in data store
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
        token_info - Set on first call to get_access_token and updated on following calls when refresh is needed
        """
        self.username = username
        self.db_creds = db_creds
        self.spotify_app_creds = spotify_app_creds
        self.token_info = None

    def is_token_expired(self):
        now = int(time.time())
        return int(self.token_info['expires_at']) < now

    def get_access_token(self):
        """
        Query DB for tokens, if token is expired, get refresh it and update DB.
        """
        self.token_info = self.get_tokens_for_user()

        if self.is_token_expired():
            print('UPDATING TOKEN')
            new_token_info = self.refresh_access_token(self.token_info['refresh_token'])

            print('token object returned from spotify api')
            print(new_token_info)

            success = self.update_token_for_user(new_token_info)
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
        client_id = self.spotify_app_creds['SPOTIFY_CLIENT_ID']
        client_secret = self.spotify_app_creds['SPOTIFY_CLIENT_SECRET']
        auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}


    # Functions that access MySQL


    def conn(self):
        return MySQLdb.connect(
            host=self.db_creds['DB_HOST'],
            user=self.db_creds['DB_USER'],
            passwd=self.db_creds['DB_PASS'],
            db=self.db_creds['DB_NAME']
        )

    def get_tokens_for_user(self):
        con = self.conn()
        cur = MySQLdb.cursors.DictCursor(con)
        cur.execute("""
            SELECT 
                spotify_auth_token, 
                spotify_refresh_token, 
                expires_at
            FROM users
                WHERE username =%s
            """, (self.username,))
        result = cur.fetchone()
        if not result:
            print('did not find user in db, exiting')
            sys.exit(1)
        else:
            user = dict()
            user['refresh_token'] = result['spotify_refresh_token']
            user['access_token'] = result['spotify_auth_token']
            user['expires_at'] = result['expires_at']
            return user

    def update_token_for_user(self, new_token_info):
        con = self.conn()
        cur = MySQLdb.cursors.DictCursor(con)
        cur.execute("""
            UPDATE users
            SET 
                spotify_auth_token = %s,
                expires_at = %s
            WHERE username = %s
            """, (new_token_info['access_token'], str(new_token_info['expires_at']), self.username,))
        con.commit()
