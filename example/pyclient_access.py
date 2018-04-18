# -*- coding: utf-8 -*-
"""
Have a look at the https://github.com/oisinmulvihill/apiaccesstoken for usage
instructions.

Oisin Mulvihill
2016-04-22

"""
from urlparse import urljoin
import requests
from apiaccesstoken.clientside import RequestsAccessTokenAuth


class Client(object):
    """A client REST API lib example using apiaccesstoken.clientside togther
    with the excellent Requests library.
    """
    def __init__(self, uri="http://localhost:8080"):
        self.base_uri = uri
        # In a real app this would come from config:
        from pyramid_webapp import API_ACCESS_TOKEN
        self.auth = RequestsAccessTokenAuth(API_ACCESS_TOKEN)
        print("REST Service base URI: {}".format(self.base_uri))

    def public(self, name="bob"):
        """Access the public page."""
        resp = requests.get(urljoin(self.base_uri, 'public/{}'.format(name)))
        resp.raise_for_status()
        print(resp.content)

    def private(self, name="bob"):
        """Access the private page."""
        resp = requests.get(
            urljoin(self.base_uri, 'private/{}'.format(name)),
            auth=self.auth
        )
        resp.raise_for_status()
        print(resp.content)


if __name__ == '__main__':
    api = Client()
    api.public()
    api.private()
