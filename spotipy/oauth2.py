
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


class SpotifyOauthError(Exception):
    pass


# TODO: set client and secret id in env

class SpotifyClientCredentials(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, user_id):
        """
        user_id - id to match entries for user in data store.
        token_info - Set on first call to get_access_token and updated on following calls when refresh is needed
        """
        self.token_info = None

    def is_token_expired(self, token_info):
        now = int(time.time())
        return (token_info['expires_at'] - now) < 60

    def get_access_token(self):
        """
        Query database for token and last updated
        """
        ''' TODO:
        # set 'expires_at', 'refresh_token', and 'access_token'
        token_info = get_token_data()
        if token_info['expires_at'] < ( now - 60):
            # get a new one
            token_info = self.refresh_access_token(token_info['refresh_token'])
            # update db
        if self.token_info and not self.is_token_expired(self.token_info):
            return self.token_info['access_token']
        '''
        # TODO remove stub
        token_info = dict()
        token_info['access_token'] = ''
        token_info['refresh_token'] = ''

        token_info = self.refresh_access_token(token_info['refresh_token'])

        self.token_info = token_info
        return self.token_info['access_token']

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
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
        return os.getenv('SPOTIPY_CLIENT_ID')

    @staticmethod
    def get_client_secret():
        return os.getenv('SPOTIPY_CLIENT_SECRET')


# I do not use this in any way. I assume that tokens and refresh are 
# fetchable via the functions: .
class SpotifyOAuth(object):
    '''
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    '''

    OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, redirect_uri,
            state=None, scope=None, proxies=None):
        '''
            Creates a SpotifyOAuth object

            Parameters:
                 - client_id - the client id of your app
                 - client_secret - the client secret of your app
                 - redirect_uri - the redirect URI of your app
                 - state - security state
                 - scope - the desired scope of the request
        '''

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state=state
        self.scope=self._normalize_scope(scope)
        self.proxies = proxies

    def _is_scope_subset(self, needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split()) if needle_scope else set()
        haystack_scope = set(haystack_scope.split()) if haystack_scope else set()
        return needle_scope <= haystack_scope

    def is_token_expired(self, token_info):
        return is_token_expired(token_info)

    def get_authorize_url(self, state=None, show_dialog=False):
        """ Gets the URL to use to authorize this app
        """
        payload = {'client_id': self.client_id,
                   'response_type': 'code',
                   'redirect_uri': self.redirect_uri}
        if self.scope:
            payload['scope'] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload['state'] = state
        if show_dialog:
            payload['show_dialog'] = True

        urlparams = urllibparse.urlencode(payload)

        return "%s?%s" % (self.OAUTH_AUTHORIZE_URL, urlparams)

    def parse_response_code(self, url):
        """ Parse the response code in the given response url

            Parameters:
                - url - the response url
        """

        try:
            return url.split("?code=")[1].split("&")[0]
        except IndexError:
            return None

    def _make_authorization_headers(self):
        return _make_authorization_headers(self.client_id, self.client_secret)

    def get_access_token(self, code):
        """ Gets the access token for the app given the code

            Parameters:
                - code - the response code
        """

        payload = {'redirect_uri': self.redirect_uri,
                   'code': code,
                   'grant_type': 'authorization_code'}
        if self.scope:
            payload['scope'] = self.scope
        if self.state:
            payload['state'] = self.state

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, verify=True, proxies=self.proxies)
        if response.status_code != 200:
            raise SpotifyOauthError(response.reason)
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        return token_info

    def _normalize_scope(self, scope):
        if scope:
            scopes = scope.split()
            scopes.sort()
            return ' '.join(scopes)
        else:
            return None

    def refresh_access_token(self, refresh_token):
        payload = { 'refresh_token': refresh_token,
                   'grant_type': 'refresh_token'}

        headers = self._make_authorization_headers()

        response = requests.post(self.OAUTH_TOKEN_URL, data=payload,
            headers=headers, proxies=self.proxies)
        if response.status_code != 200:
            if False:  # debugging code
                print('headers', headers)
                print('request', response.url)
            self._warn("couldn't refresh token: code:%d reason:%s" \
                % (response.status_code, response.reason))
            return None
        token_info = response.json()
        token_info = self._add_custom_values_to_token_info(token_info)
        if not 'refresh_token' in token_info:
            token_info['refresh_token'] = refresh_token
        return token_info

    def _add_custom_values_to_token_info(self, token_info):
        '''
        Store some values that aren't directly provided by a Web API
        response.
        '''
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        token_info['scope'] = self.scope
        return token_info

    def _warn(self, msg):
        print('warning:' + msg, file=sys.stderr)

