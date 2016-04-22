# -*- coding: utf-8 -*-
"""
"""
import os
import hashlib

import tokenlib


class AccessTokenInvalid(Exception):
    """Raised when an access_token can't be verified."""


class Manager(object):
    """
    """
    SECRET_LENGTH = 64

    def __init__(self, secret, timeout=10):
        """
        """
        self.timeout = timeout
        self.tman = tokenlib.TokenManager(
            secret=secret,
            # I want non expiring tokens for now. A hack is to set this to
            # a value higher then 'now' used when verifing.
            timeout=timeout,
            # Set to the strongest has available in py2.7 which we should
            # review every so often.
            hashmod=hashlib.sha512,
        )

    @classmethod
    def generate_secret(cls):
        """Generate a master secret that can be used in Manager's config.
        """
        return os.urandom(cls.SECRET_LENGTH).encode('hex')

    def generate_access_token(self, identity):
        """Generate an access token which can later be verified.
        """
        # for the expiry to 10 as I parse it with 5 so it won't expire
        # for the moment.
        payload = {}
        payload['expires'] = self.timeout
        payload['identity'] = identity

        return self.tman.make_token(payload)

    def verify_access_token(self, access_token):
        """Get the payload verifying the access token.

        Currently tokens don't expire.

        :returns: A dict payload which was in the access_token.

        """
        try:
            payload = self.tman.parse_token(access_token, now=5)

        except ValueError, e:
            raise AccessTokenInvalid(e)

        return payload
