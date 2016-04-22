# -*- coding: utf-8 -*-
"""
Have a look at the https://github.com/oisinmulvihill/apiaccesstoken for usage
instructions.

Oisin Mulvihill
2016-04-22

"""
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from apiaccesstoken.middleware import UserAccess
from apiaccesstoken.exceptions import HTTPForbidden
from apiaccesstoken.middleware import TokenMiddleware

# My user "database":
#
USERS = {
    "user_00ca4f6190b84f25827239233c4bcbaa": {
        "id": "user_00ca4f6190b84f25827239233c4bcbaa",
        "username": "bob",
        "access_token": (
            "eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjA5NDU1ZiIsICJpZGVudGl0eSI6ICJib"
            "2Iifa3w0hzmNrThx3-PUlyidFWYw1Bx00OXdk2Iq4b48fEF0Ts3nLOliryX-4-wxL"
            "gmo5PRyivKNrAFvGhsaWq3yL8="
        ),
        "access_secret": (
            "f7e118ff011236a38b38c4909045c9cc5794aa7e490d4fab777de0ff801539f1f"
            "4152129e5588a0dcabb3848798c6dca958554146f9e14a10e0325bc43f7111d"
        )
    }
}

NAME_TO_ID = {"bob": "user_00ca4f6190b84f25827239233c4bcbaa"}

TOKEN_TO_SECRET = {
    USERS[NAME_TO_ID['bob']]['access_token']: (
        USERS[NAME_TO_ID['bob']]['access_secret']
    )
}

API_ACCESS_TOKEN = USERS[NAME_TO_ID['bob']]['access_token']


class Token(TokenMiddleware):
    def recover_secret(self, access_token):
        print("looking for secret with access_token '{}'".format(access_token))
        return TOKEN_TO_SECRET.get(access_token)


class Access(UserAccess):

    @classmethod
    def recover_user(cls, identifier):
        print("recover_user by identifier '{}'".format(identifier))
        found = None

        if USERS.get(identifier):
            found = USERS.get(identifier)

        if NAME_TO_ID.get(identifier):
            found = USERS.get(NAME_TO_ID.get(identifier))

        # helpful debug
        print("For identifier '{}' I found {}".format(
            identifier,
            "Nothing :(" if found is None else found
        ))

        if found is None:
            raise HTTPForbidden()

        return found


@Access.auth_required
def private_view(request):
    # auth OK at this point, recover the logged-in user details:
    userd = Access.user_for_login(request)
    print("user details: {}".format(userd))

    return Response('Hello Private Member %(name)s!' % request.matchdict)


def public_view(request):
    return Response('Hello %(name)s!' % request.matchdict)


if __name__ == '__main__':
    config = Configurator()
    config.add_route('public', '/public/{name}')
    config.add_view(public_view, route_name='public')
    config.add_route('private', '/private/{name}')
    config.add_view(private_view, route_name='private')
    app = config.make_wsgi_app()
    # Enable token access:
    app = Token(app)
    server = make_server('0.0.0.0', 8080, app)
    print("Running on http://0.0.0.0:8080 (Ctrl-C to exit).")
    server.serve_forever()
