# -*- coding: utf-8 -*-
"""
The API Access Token Header to look for in a pyramid/wsgi environment stack.

Oisin Mulvihill
2014-03-06

"""

# The exact header to set via CURL or HTTPie:
ACCESS_TOKEN_HEADER = "AUTHORIZATION"

# How the header will show up in the Wsgi environment dict:
WSGI_ENV_ACCESS_TOKEN_HEADER = "HTTP_AUTHORIZATION"
