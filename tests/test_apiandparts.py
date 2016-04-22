# -*- coding: utf-8 -*-
"""
"""
import pytest

from apiaccesstoken import tokenmanager
from apiaccesstoken.headers import WSGI_ENV_ACCESS_TOKEN_HEADER
from apiaccesstoken.middleware import UserAccess
from apiaccesstoken.exceptions import HTTPForbidden
from apiaccesstoken.middleware import TokenMiddleware


class MockApp(object):
    """Mock wsgi app."""

    def __call__(self, environ, start_response):
        pass


def test_token_middleware(logger):
    """Test the middleware ValidateAccessToken usage.
    """
    username = 'fran'
    access_secret = tokenmanager.Manager.generate_secret()
    man = tokenmanager.Manager(access_secret)
    access_token = man.generate_access_token(identity=username)

    TOKEN_TO_SECRET = {access_token: access_secret}

    class MyTokenMiddleware(TokenMiddleware):
        def __init__(self, app):
            super(MyTokenMiddleware, self).__init__(app)
            self.recover_secret_called = False
            self.access_secret = None
            self.access_token_given = None

        def recover_secret(self, access_token):
            self.access_token_given = access_token
            self.access_secret = TOKEN_TO_SECRET.get(access_token)
            return self.access_secret

    app = MockApp()
    app = MyTokenMiddleware(app)

    assert app.access_secret is None
    assert app.access_token_given is None

    assert MyTokenMiddleware.ENV_KEY == 'apitokenaccess_identity'

    environ = {}
    start_response = lambda x: x

    # make a wsgi call which will result in no action:
    app(environ, start_response)

    # check nothing has changed:
    assert app.access_secret is None
    assert app.access_token_given is None
    assert MyTokenMiddleware.ENV_KEY not in environ

    # Now provide and access token which is valid:
    #
    environ[WSGI_ENV_ACCESS_TOKEN_HEADER] = access_token
    app(environ, start_response)

    # Now the identity should have been recovered and set in the env:
    assert app.access_secret == access_secret
    assert app.access_token_given == access_token
    assert MyTokenMiddleware.ENV_KEY in environ
    assert environ[MyTokenMiddleware.ENV_KEY] == username


def test_token_middleware_empty_env():
    """Test nothing is found in an empty environment.
    """
    environ = {}
    start_response = lambda x: x

    class MyTokenMiddleware(TokenMiddleware):
        def __init__(self, app):
            super(MyTokenMiddleware, self).__init__(app)
            self.recover_secret_called = False
            self.access_secret = None
            self.access_token_given = None

        def recover_secret(self, access_token):
            self.access_token_given = access_token
            self.access_secret = None
            return self.access_secret

    app = MockApp()
    app = MyTokenMiddleware(app)

    assert app.access_secret is None
    assert app.access_token_given is None
    assert MyTokenMiddleware.ENV_KEY not in environ

    # make a wsgi call which will result in no action:
    app(environ, start_response)

    # check nothing has changed:
    assert app.access_secret is None
    assert app.access_token_given is None
    assert MyTokenMiddleware.ENV_KEY not in environ


def test_header_token_extract_re_matching():
    """Test the middleware ValidateAccessToken usage.
    """
    username = 'fran'
    access_secret = tokenmanager.Manager.generate_secret()
    man = tokenmanager.Manager(access_secret)
    access_token = man.generate_access_token(identity=username)

    TOKEN_TO_SECRET = {access_token: access_secret}

    class MyTokenMiddleware(TokenMiddleware):
        def __init__(self, app):
            super(MyTokenMiddleware, self).__init__(app)
            self.recover_secret_called = False
            self.access_secret = None
            self.access_token_given = None

        def recover_secret(self, access_token):
            self.access_token_given = access_token
            self.access_secret = TOKEN_TO_SECRET.get(access_token)
            return self.access_secret

    app = MockApp()
    app = MyTokenMiddleware(app)

    # Test out the extract token on different Header value types:
    #
    found = app.token_extract("Token {}".format(access_token))
    assert found == access_token

    found = app.token_extract("{}".format(access_token))
    assert found == access_token

    found = app.token_extract("")
    assert found == ""


def test_ValidateAccessToken_invalid_secret():
    """Test the middleware ValidateAccessToken usage.
    """
    username = 'fran'
    access_secret = tokenmanager.Manager.generate_secret()
    man = tokenmanager.Manager(access_secret)
    access_token = man.generate_access_token(identity=username)
    start_response = lambda x: x
    environ = {
        WSGI_ENV_ACCESS_TOKEN_HEADER: access_token
    }

    class MyTokenMiddleware(TokenMiddleware):
        def __init__(self, app):
            super(MyTokenMiddleware, self).__init__(app)
            self.recover_secret_called = False
            self.access_secret = "the wrong secret"
            self.access_token_given = None

        def recover_secret(self, access_token):
            self.access_token_given = access_token
            return self.access_secret

    app = MockApp()
    app = MyTokenMiddleware(app)
    assert app.access_secret == "the wrong secret"
    assert app.access_token_given is None

    app(environ, start_response)

    # The identity should not be in the environment as the payload won't
    # have been recovered, the secret should not have been able to decode
    # the token.
    assert app.access_secret == "the wrong secret"
    assert app.access_token_given == access_token
    assert TokenMiddleware.ENV_KEY not in environ


def test_tokenmanager():
    """Test the basic usage and calls of the manager.
    """
    username = 'fran'

    secret = tokenmanager.Manager.generate_secret()

    man = tokenmanager.Manager(secret)

    # Generate an access_token, this needs the master secret set so can't be
    # a class
    access_token = man.generate_access_token(identity=username)

    # Some time later...

    # Now verify the access token
    man1 = tokenmanager.Manager(secret)

    payload = man1.verify_access_token(access_token)

    #print "payload: ", payload

    assert payload['identity'] == username
    # Hard coded for the moment as I'm forcing tokens not to expire.
    assert payload['expires'] == 10

    # an invalid token will raise and exception
    with pytest.raises(tokenmanager.AccessTokenInvalid):
        man1.verify_access_token("some token I've just made up.")

    # the master secret needs to be the same as that generating secrets:
    with pytest.raises(tokenmanager.AccessTokenInvalid):
        man2 = tokenmanager.Manager("the wrong secret key")
        man2.verify_access_token(access_token)
