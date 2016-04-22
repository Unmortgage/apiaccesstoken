# -*- coding: utf-8 -*-
"""
"""
try:
    from pyramid.httpexceptions import HTTPForbidden

except ImportError, e:

    class HTTPForbidden(Exception):
        """403 Access Denied."""
