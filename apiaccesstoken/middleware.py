# -*- coding: utf-8 -*-
"""
"""
import re
import logging
from functools import wraps

from apiaccesstoken.tokenmanager import Manager
from apiaccesstoken.exceptions import HTTPForbidden
from apiaccesstoken.tokenmanager import AccessTokenInvalid
from apiaccesstoken.headers import WSGI_ENV_ACCESS_TOKEN_HEADER


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


class TokenMiddleware(object):
    """Validate and API access token and populate the wsgi environment with
    the identity recovered.

    headers.HTTP_HEADER is the name of the wsgi env variable to look for.

    self.ENV_KEY is the name wsgi env variable to store the identity in. The
    value of the identity is recovered from the 'identity' field in the
    access_token payload.

    The constructor for this class takes a recover_secret() function. This
    needs to be provided or NotImplementedError will be raised. This function
    recovers the access_secret for the given access_token if any. If this
    function returns None then nothing was recovered and the token is invalid.

    """
    WITHTOKEN_RE = re.compile("(Token\s*)(.*)")

    # The wsgi environment variable to set when an identity was found:
    ENV_KEY = 'apitokenaccess_identity'

    def __init__(self, application):
        self.application = application

    def recover_secret(self, access_token):
        """Recover the secret token for the given access_token.

        The end-developer must override to provide the functionality needed.

        :param access_token: The access token string to search for with.

        :returns: the secret token string or None if nothing was found.

        """
        raise NotImplementedError('No Valid Access Detail Recovery Provided')

    def recover_access(self, environ, access_token):
        """Populate the environment with the user identity recovered from the
        payload of the access_token.

        To get the payload the access_token needs its corresponding
        access_secret to recover it.

        """
        log = get_log('headers.recover_access')

        partial_tk = "{}..<hidden>..{}".format(
            access_token[:4], access_token[-4:]
        )
        log.debug(
            "recover_secret: access_token {}".format(partial_tk)
        )

        try:
            access_secret = self.recover_secret(access_token)
            if access_secret:
                log.debug(
                    "access_secret for access_token:{} recovered OK.".format(
                        partial_tk
                    )
                )
                man = Manager(access_secret)
                payload = man.verify_access_token(access_token)
                log.debug(
                    "Payload recovered '{}'. Looking for identity.".format(
                        partial_tk
                    )
                )

                identity = payload['identity']
                log.debug(
                    "Token Valid. Adding identity '{}' environ.".format(
                        identity
                    )
                )
                environ[self.ENV_KEY] = identity

            else:
                log.info(
                    (
                        "No secret recovered for access_token '{}'. "
                        "Ignoring token."
                    ).format(
                        partial_tk
                    )
                )

        except AccessTokenInvalid as error:
            log.error(
                "token validation fail: '{}'".format(error)
            )

    def token_extract(self, header_value):
        """Handle 'Token <data>' or '<data>' values in the auth header content.

        :returns: the <data> bit of the header_value.

        """
        access_token = ""

        with_token = re.match(self.WITHTOKEN_RE, header_value)
        if with_token:
            access_token = with_token.groups()[1]

        else:
            access_token = header_value.strip()

        return access_token

    def __call__(self, environ, start_response):
        """Wsgi hook into kicking off the token validation and identity
        recovery.

        """
        log = get_log("headers")

        access_token = environ.get(WSGI_ENV_ACCESS_TOKEN_HEADER)
        if not access_token:
            access_token = environ.get("HTTP_AUTHORIZATION")

        if access_token:
            partial_tk = "{}..<hidden>..{}".format(
                access_token[:4], access_token[-4:]
            )
            log.debug("found access_token {}".format(partial_tk))
            # String out the "Token " from the "Token <token key>" from the
            # HTTP_AUTHORIZATION string.
            access_token = self.token_extract(access_token)
            self.recover_access(environ, access_token)

        return self.application(environ, start_response)


class UserAccess(object):
    """Pyramid View Decorator to enforce authentiction being required.

    The end-developer needs to implement recover_user to return the required
    user's details.

    """
    @classmethod
    def recover_user(cls, identifier):
        """Recover a user for a given identifier.

        :param identifier: A string either the username or unique ID.

        :returns: The user dict or None if nothing was found.

        """
        raise NotImplementedError(
            'No Access Details for identity {} can be found.'.format(
                identifier
            )
        )

    @classmethod
    def user_for_login(cls, request):
        """Recover the logged in user for auth or token access.

        If no user_id/username/identifer was recovered from the environment
        then HTTPForbidden will be raised as a login is required.

        This will look at the request environment for the following keys.

        1. repoze.who.identity:

        If present the 'repoze.who.identity' will be used if present. If
        not then 'username' will be ised.

        2. TokenMiddleware.ENV_KEY:

        A api access token identity identifier.

        If neither of the above could be found then HTTPForbidden will be
        raised and cls.recover_user will not get called.

        :returns: The result of cls.recover_user(identifier).

        """
        log = get_log("user_for_login")
        identifier = None

        # standard repoze related identity:
        if 'repoze.who.identity' in request.environ:
            identity = request.environ['repoze.who.identity']

            if 'username' in identity:
                identifier = identity['username']

            elif 'repoze.who.userid' in identity:
                identifier = identity['repoze.who.userid']

        # token based identity:
        elif TokenMiddleware.ENV_KEY in request.environ:
            identifier = request.environ[TokenMiddleware.ENV_KEY]

        else:
            log.debug("No identifier recovered from environment!")

        if not identifier:
            raise HTTPForbidden()

        return cls.recover_user(identifier)

    @classmethod
    def auth_required(cls, f):
        """A pyramid view based decorator to restrict access to only
        authorised users.

        This calls user_for_login(request) to make sure there is an authorised
        user is present. If not then exceptions.HTTPForbidden will be raised.

        This will attempt to look for valid token or web-session based
        identities in the request environment. If a valid token has been used
        one will be present.

        """
        @wraps(f)
        def decorated_function(request, *args, **kwargs):
            """Wrap view with a call to user_for_login first."""
            cls.user_for_login(request)
            return f(request, *args, **kwargs)

        return decorated_function
