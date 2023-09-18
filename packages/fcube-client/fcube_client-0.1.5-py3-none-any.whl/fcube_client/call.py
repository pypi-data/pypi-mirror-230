#!/usr/bin/env python

import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_oauthlib import OAuth1, OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from math import floor
from datetime import datetime, timedelta
import json
import yaml
import logging
import os
import sys
from enum import Enum

from .printer import Printer

# Set URL for the client
URL = 'http://localhost:3000'

class AuthenticationError(Exception):
    pass


AuthType = Enum('AuthType', 'HTTPBASICAUTH HTTPDIGESTAUTH OAUTH1 OAUTH2 NONE')

printer = Printer()

class FiddleCube(object):
    def __init__(
        self,
        user=None,
        password=None,
        client_app_key=None,
        client_app_secret=None,
        user_oauth_token=None,
        user_oauth_token_secret=None,
        api_app_key=None,
        auth_type=None,
        fc_api_token=None,
        fc_app_id=None
    ):
        '''Set up client for API communications
           This is where you'll need to specify all the authentication and
           required headers

           Preference will be given towards passed in variables, otherwise
           environment variables will be used

           Config file is supported but discouraged since it's a common
           source of credential leaks
        '''
        # Setup Host here
        self.url = URL
        # Setup Session object for all future API calls
        self.session = requests.Session()
        self.fc_api_token = fc_api_token
        self.fc_app_id = fc_app_id

        # Setup authentication
        # If interested in using a config file instead of env vars, load with
        # self._load_key_yml(config_key, path)
        # Feel free to clear out auth methods not implemented by the API
        
        if not auth_type:
            auth_type = AuthType[os.getenv('AUTH_TYPE', default='NONE')]
        if (auth_type == AuthType.HTTPBASICAUTH or
                auth_type == AuthType.HTTPDIGESTAUTH):
            if not user:
                user = os.getenv('CLIENT_USER')
            if not password:
                password = os.getenv('CLIENT_PASSWORD')
            if auth_type == AuthType.HTTPBASICAUTH:
                self.session.auth = HTTPBasicAuth(user, password)
            else:
                self.session.auth = HTTPDigestAuth(user, password)
        if auth_type == AuthType.OAUTH1:
            if not client_app_key:
                client_app_key = os.getenv('CLIENT_APP_KEY')
            if not client_app_secret:
                client_app_secret = os.getenv('CLIENT_APP_SECRET')
            if not user_oauth_token:
                user_oauth_token = os.getenv('USER_OAUTH_TOKEN')
            if not user_oauth_token_secret:
                user_oauth_token_secret = os.getenv('USER_OAUTH_TOKEN_SECRET')
            self.session.auth = OAuth1(
                client_app_key,
                client_app_secret,
                user_oauth_token,
                user_oauth_token_secret
            )
        if auth_type == AuthType.OAUTH2:
            # Feel free to create a PR if you want to contribute
            # if not client_app_key:
            #     client_app_key = os.getenv('CLIENT_APP_KEY')
            # if not client_app_secret:
            #     client_app_secret = os.getenv('CLIENT_APP_SECRET')
            # if not authorization_redirect_url:
            #     authorization_redirect_url = os.getenv('CLIENT_REDIRECT_URL')
            # if not user_oauth_token_secret:
            #     user_oauth_token_secret = os.getenv('USER_OAUTH_TOKEN_SECRET')
            # client = BackendApplicationClient(client_id=CLIENT_APP_KEY)
            # oauth = OAuth2Session(client=client)
            # token = oauth.fetch_token(token_url='https://github.com/login/oauth/access_token', 
            #                           client_id=client_app_key, client_secret=client_app_secret)
            
            raise NotImplementedError("OAuth2 currently not supported")

        # Some APIs require an API key in a header in addition to or instead
        # of standard authentication methods
        if not api_app_key:
            api_app_key = os.getenv('API_APP_KEY')
        self.session.headers.update({'App-Key': api_app_key})

        # Setup any additional headers required by the API
        # This sometimes includes additional account info
        account_owner = os.getenv('PINGDOM_ACCOUNT_OWNER')
        if account_owner:
            self.session.headers.update({'account-email': account_owner})

        printer.logger.info('Authenticating...')
        if self._authenticate():
            printer.logger.info('Authentication Successful!')
        else:
            printer.logger.info('Authentication Failed!')
            raise AuthenticationError('Authentication Failed!')

    def _load_key_yml(self, config_key, path):
        '''Example function for loading config values from a yml file
        '''
        with open(path) as stream:
            yaml_data = yaml.safe_load(stream)
            return yaml_data[config_key]

    def _authenticate(self):
        '''Authenticate by making simple request
           Some APIs will offer a simple auth validation endpoint, some
           won't.
           I like to make the simplest authenticated request when
           instantiating the client just to make sure the auth works
        '''
        return True

    def _make_request(self, endpoint, method, query_params=None, body=None):
        '''Handles all requests to Pingdom API
        '''
        url = self.url + endpoint
        req = requests.Request(method, url, params=query_params, json=body)

        prepped = self.session.prepare_request(req)
        
        # Add bearer token
        prepped.headers['FC_API_KEY'] = f"{self.fc_api_token}"

        # Log request prior to sending
        printer._pprint_request(prepped)

        # Actually make request to endpoint
        r = self.session.send(prepped)

        # Log response immediately upon return
        printer._pprint_response(r)

        # Handle all response codes as elegantly as needed in a single spot
        if r.status_code == requests.codes.ok:
            try:
                resp_json = r.json()
                printer.logger.info('Response: {}'.format(resp_json))
                return resp_json
            except ValueError:
                return r.text

        elif r.status_code == 401:
            printer.logger.info("Authentication Unsuccessful!")
            try:
                resp_json = r.json()
                printer.logger.debug('Details: ' + str(resp_json))
                raise AuthenticationError(resp_json)
            except ValueError:
                raise

        # TODO handle rate limiting gracefully

        # Raises HTTP error if status_code is 4XX or 5XX
        elif r.status_code >= 400:
            printer.logger.error('Received a ' + str(r.status_code) + ' error!')
            try:
                printer.logger.debug('Details: ' + str(r.json()))
            except ValueError:
                pass
            r.raise_for_status()

    def make_request(
        self,
        endpoint,
        method="GET",
        query_params=None,
        body=None
    ):
        return self._make_request(endpoint, method, query_params, body)

    def collect(self, payload):
        # collect input output prompts
        # Make body payload with bearer token
        endpoint = '/v1/prompts/collect'
        payload['applicationId'] = payload.get('fc_app_id', self.fc_app_id)
        self.make_request(endpoint, method="POST", body=payload)
    


if __name__ == "__main__":
    fc = FiddleCube(
        fc_api_token=os.getenv('FIDDLECUBE_API_TOKEN', default=None),
        fc_app_id=os.getenv('FIDDLECUBE_APP_ID', default=None)
    )
    from_datetime = datetime.now()
    to_datetime = datetime.now() + timedelta(1)
    payload = {
        "input": 'Some input for the model',
        "prompt": 'Some prompt',
        "query": 'Some query passed by user',
        "output": 'Some output of the model',
        "metadata": {
            "uno": 1,
            "dos": 2
        }
    }
    fc.collect(payload)