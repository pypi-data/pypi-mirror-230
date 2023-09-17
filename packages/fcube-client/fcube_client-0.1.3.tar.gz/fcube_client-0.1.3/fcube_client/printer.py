#!/usr/bin/env python

from math import floor
import logging
import os
import sys


# Set up basic logger
logger = logging.getLogger('example.exampleClient')

# Setup stdout logger
soh = logging.StreamHandler(sys.stdout)
# Can optionally set logging levels per handler
# soh.setLevel(logging.WARN)
logger.addHandler(soh)

# File handler for logging to a file
# fh = logging.FileHandler('apiWrapper.log')
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)

# Get log level from env vars
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
if os.environ.get('DEBUG'):
    if log_level:
        logger.warn("Overriding LOG_LEVEL setting with DEBUG")
    log_level = 'DEBUG'

try:
    logger.setLevel(log_level)
except ValueError:
    logger.setLevel(logging.INFO)
    logger.warn("Variable LOG_LEVEL not valid - Setting Log Level to INFO")


class Printer(object):
    def __init__(
        self
    ):
        '''Set up client for API communications
           This is where you'll need to specify all the authentication and
           required headers

           Preference will be given towards passed in variables, otherwise
           environment variables will be used

           Config file is supported but discouraged since it's a common
           source of credential leaks
        '''
        # Setup Session object for all future API calls
        self.logger = logger
        self

    def _pprint_request(self, prepped):
        '''
        method endpoint HTTP/version
        Host: host
        header_key: header_value

        body
        '''
        method = prepped.method
        url = prepped.path_url
        # TODO retrieve HTTP version
        headers = '\n'.join('{}: {}'.format(k, v) for k, v in
                            prepped.headers.items())
        # Print body if present or empty string if not
        body = prepped.body or ""
        logger.info("Requesting {} to {}".format(method, url))
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            method + ' ' + url,
            ' ' + headers,
            body,
        ))
        logger.debug(
            '{}\n{} {} HTTP/1.1\n{}\n\n{}'.format(
                '-----------REQUEST-----------',
                method,
                url,
                headers,
                body
            )
        )

    def _pprint_response(self, r):
        '''
        HTTP/version status_code status_text
        header_key: header_value

        body
        '''
        # Not using requests_toolbelt.dump because I want to be able to
        # print the request before submitting and response after
        # ref: https://stackoverflow.com/a/35392830/8418673

        httpv0, httpv1 = list(str(r.raw.version))
        httpv = 'HTTP/{}.{}'.format(httpv0, httpv1)
        status_code = r.status_code
        status_text = r.reason
        headers = '\n'.join('{}: {}'.format(k, v) for k, v in
                            r.headers.items())
        body = r.text or ""
        # Convert timedelta to milliseconds
        elapsed = floor(r.elapsed.total_seconds() * 1000)

        logger.info(
            "Response {} {} received in {}ms".format(
                status_code,
                status_text,
                elapsed
            )
        )

        logger.debug(
            '{}\n{} {} {}\n{}\n\n{}'.format(
                '-----------RESPONSE-----------',
                httpv,
                status_code,
                status_text,
                headers,
                body
            )
        )