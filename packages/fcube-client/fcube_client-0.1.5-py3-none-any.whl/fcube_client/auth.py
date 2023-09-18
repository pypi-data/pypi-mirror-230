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


class Auth(object):
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
        self
