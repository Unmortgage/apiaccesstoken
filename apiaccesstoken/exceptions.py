# -*- coding: utf-8 -*-
"""
"""
try:
    from pyramid.httpexceptions import HTTPForbidden

except ImportError:

    class HTTPForbidden(Exception):
        """403 Access Denied."""
