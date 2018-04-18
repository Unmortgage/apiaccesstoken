apiaccesstoken
==============

.. image:: https://travis-ci.org/oisinmulvihill/apiaccesstoken.svg?branch=master
    :target: https://travis-ci.org/oisinmulvihill/apiaccesstoken

.. contents::

Introduction
------------

*note*: I no longer support Python 2 and have upgraded this to work with Python 3

Secure token authorisation for Pyramid / Repoze based webapps. It uses
Mozilla's tokenlib_ to provide strong protection.

This library provides the middleware and token validation. It does not provide
a token / user detail storage backend. It allows you to configure callbacks
to interface to any system you may be using. I prefer the greater flexibility
this gives.

This project was originally known as pp-apiaccesstoken_. I created it as a
quick yet secure way to provide token authentication. You could then decided
to move to full OAuth 2 or other approaches later on. I've moved to using
:ref:`JSON Web Token (JWT) <jwt>` nowadays. However this libray files a niche
where I wish to protect a demo or light-weight REST API.


Usage Example
-------------

Have a look at source code in the example directory. The pyramid_webapp.py is
an example of how to integrate into a Pyramid webapp. The pyclient_access.py is
an example of a basic client library to access the service.

To run the example service install Pyramid and then run the webapp e.g.::

    # from apiaccesstoken dir
    #
    python setup.py develop

    # get Pyramid:
    pip install Pyramid

    # Run the webapp
    python example/pyramid_webapp.py

You should see::

    $ python example/pyramid_webapp.py
    Running on http://0.0.0.0:8080 (Ctrl-C to exit).

Now in another terminal window you can call the python client lib to access
the running webapp API::

    # from apiaccesstoken dir
    #
    $ python example/pyclient_access.py
    REST Service base URI: http://localhost:8080
    Hello bob!
    Hello Private Member bob!

    $

Success! Now if you wanted to talk to the API using cURL you would do the
following from the command line::

    # Access the public view without needed to use the token:
    #
    $ curl http://localhost:8080/public/bob
    Hello bob!

    # Now without using then access token, attempt to gain access to the
    # private view:
    #
    $ curl http://localhost:8080/private/bob
    <html>
     <head>
      <title>403 Forbidden</title>
     </head>
     <body>
      <h1>403 Forbidden</h1>
      Access was denied to this resource.<br/><br/>
     </body>
    </html>

    # Great, the private view is protected. Now using the access token, gain
    # access to the private view:
    #
    $ TOKEN="eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjFhNDg2NiIsICJpZGVudGl0eSI6ICJwbmNhbmFseXRpY3MifQOtFroyPKR6UKIXevPytLKhKQ6A02r70swutaZkJMgX3iCPWoUw1VK-BR81frJLrWajF4pmpqnTSuNhXl7tcpw="
    $ curl -H "AUTHORIZATION: Token $TOKEN" http://localhost:8080/private/bob
    Hello Private Member bob!

    $

Success! Now lets try to access the service with a token we know nothing about::

    $ TOKEN="eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjAxOTdlZiIsICJpZGVudGl0eSI6ICJhbGljZSJ9yaJ_zX9TIfC650kbhiE1mS3GfYME6sZZ7IYP6s4BY0cADrqHd_yaVISnKV5E7cwT42mJjRk8_zkoesYk5YC4FA=="
    $ curl -H "AUTHORIZATION: Token $TOKEN" http://localhost:8080/private/bob
    <html>
     <head>
      <title>403 Forbidden</title>
     </head>
     <body>
      <h1>403 Forbidden</h1>
      Access was denied to this resource.<br/><br/>

     </body>
    </html>(t2)

No, no access allowed.


Generating Secret & Access Tokens
---------------------------------

When this library is set up it installs a tokenhelper command line tool. You
can look at its source code in apiaccesstoken.scripts.tokenhelper.

The tokens used in the example were generated as follows::

    # For the "bob"
    #
    $ tokenhelper make_access_secret
    New secret token is:
        f7e118ff011236a38b38c4909045c9cc5794aa7e490d4fab777de0ff801539f1f4152129e5588a0dcabb3848798c6dca958554146f9e14a10e0325bc43f7111d

    $ tokenhelper make_access_token bob f7e118ff011236a38b38c4909045c9cc5794aa7e490d4fab777de0ff801539f1f4152129e5588a0dcabb3848798c6dca958554146f9e14a10e0325bc43f7111d
    New access token is:
        eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjA5NDU1ZiIsICJpZGVudGl0eSI6ICJib2Iifa3w0hzmNrThx3-PUlyidFWYw1Bx00OXdk2Iq4b48fEF0Ts3nLOliryX-4-wxLgmo5PRyivKNrAFvGhsaWq3yL8=


    # For some unknown "alice" user presenting a token
    #
    $ tokenhelper make_access_secret
    New secret token is:
        18ad74bbf7a7678739af46a1a46119f2e3ff53da3a30a287e85ccc783010d71c00a00e910a4ba8a52f048ded16d2757df1791110776f1d0c1b5b66b2aed8eecf

    $ tokenhelper make_access_token alice 18ad74bbf7a7678739af46a1a46119f2e3ff53da3a30a287e85ccc783010d71c00a00e910a4ba8a52f048ded16d2757df1791110776f1d0c1b5b66b2aed8eecf
    New access token is:
        eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjAxOTdlZiIsICJpZGVudGl0eSI6ICJhbGljZSJ9yaJ_zX9TIfC650kbhiE1mS3GfYME6sZZ7IYP6s4BY0cADrqHd_yaVISnKV5E7cwT42mJjRk8_zkoesYk5YC4FA==

Alternatively you can generate an access token and secret pair in one step as
follows::

    $ tokenhelper make_for_username  henry
    For username 'henry' the new token pair is:
    access token is:
        eyJleHBpcmVzIjogMTAsICJzYWx0IjogIjc5ZjM3NSIsICJpZGVudGl0eSI6ICJoZW5yeSJ9TNbfsLfOaTPJFlMbFLLM6QJvK2UKc6rSeAq-1H5p-PkxWbwl2hO03LFAbFi_5taS6OqikH-KYa28FSZFnImMXA==
    access secret is:
        7730971adde5ef976fe7022e6278e46c208efcd6e8ec3dfac2727401a1c0a1f449be61e664332829d0c2ff3dac07974e0799a7695de393b41dee47138066e257


Development
-----------

Dev Env Set Up
~~~~~~~~~~~~~~

A typical dev environment for this project using Virtualenv_ and Virtualenvwrapper_ is:

.. sourcecode:: bash

    mkvirtualenv pyenv

    # cd apiaccesstoken
    python setup.py develop


Run all tests
~~~~~~~~~~~~~

From here you can do::

    workon pyenv
    pip install pytest
    py.test


.. _jwt: https://jwt.io/introduction/
.. _tokenlib: https://github.com/mozilla-services/tokenlib
.. _pp-apiaccesstoken: https://github.com/oisinmulvihill/pp-apiaccesstoken
.. _Virtualenvwrapper: https://virtualenvwrapper.readthedocs.org/en/latest/
.. _Virtualenv: https://virtualenv.pypa.io/en/latest/
