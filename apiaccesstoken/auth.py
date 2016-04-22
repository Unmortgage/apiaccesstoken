# -*- coding: utf-8 -*-
"""
"""
import logging
from functools import wraps

from apiaccesstoken.exceptions import HTTPForbidden


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


def user_for_login(request):
    """Recover the logged in user for auth or token access.

    If no user_id/username was recovered from the environment then
    HTTPForbidden will be raised as a login is required.

    If a user is found this will update their status to 'online'. Their
    status will be updated only if they were 'offline'.

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
    elif 'pp.api_access.identity' in request.environ:
        identifier = request.environ['pp.api_access.identity']

    else:
        log.debug("No identifier recovered from environment!")

    if not identifier:
        raise HTTPForbidden()

    if _USERS.get(identifier):
        found = _USERS.get(identifier)

    if _NAME_TO_ID.get(identifier):
        found = _USERS.get(_NAME_TO_ID.get(identifier))

    return found



def auth_required(f):
    """
    """
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        """Add the success status wrapper. exceptions will be
        handled elsewhere.
        """
        user_for_login(request)
        response['data'] = f(*args, **kwargs)
        response = json.dumps(response)
        return response

    return decorated_function