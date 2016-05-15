.. image:: https://travis-ci.org/jdgillespie91/twitter-ads-api.svg?branch=master
    :target: https://travis-ci.org/jdgillespie91/twitter-ads-api

==========
TwitterAds
==========

Welcome to TwitterAds; a Python wrapper around the Twitter Ads API.

The Twitter Ads API exposes a bunch of useful resources but interacting with each resource demands a certain familiarity with the API and the Twitter advertising platform. This package aims to ease that requirement where possible.

---------------
Getting started
---------------

Getting up and running is extremely easy. Install the package with

.. code:: bash

    pip install twitterads

Fetch some data with

.. code:: python

    >>> import twitterads
    >>> client = twitterads.get_client(
    ...     consumer_key='xxx',consumer_secret='xxx', access_key='xxx', access_secret='xxx'
    ... )
    >>> client.get_accounts()
    <Twitter Response [OK]>

For a more detailed guide on getting up and running, head over to `the online documentation <http://twitter-ads-api.readthedocs.org/en/latest/>`_.

----------------------------------------
Contributing and suggesting improvements
----------------------------------------

Contributions are more than welcome! Simply fork the repository, make your changes locally and open up a pull request for review. You'll find a more detailed guide on this proecdure `here <https://guides.github.com/activities/contributing-to-open-source/>`_.

If you've come across any issues or would like to suggest improvements, please open up an issue `here  <https://github.com/jdgillespie91/twitter-ads-api/issues>`_.

----------------
Acknowledgements
----------------

This library wouldn't exist without `requests <http://docs.python-requests.org/en/latest/>`_ whose model is the source of inspiration for the one you see here. Not only is the model a good one, the library is so wonderfully written that understanding it is simply a case of reading it.

--------------
Intended usage
--------------

Here, I will document by example how I want to use this package. This will aid development.

All requests should be handled by an authenticated client.

.. code:: python

    >>> client = twitterads.get_client(
    ...     client_key='...',
    ...     client_secret='...',
    ...     resource_owner_key='...',
    ...     resource_owner_secret='...'
    ... )

We should be able to instantiate a :code:`PreparedRequest` with a resource and send it via the client.

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='accounts')
    >>> client.send(request)
    <Twitter Response [OK]>

We should be able to send :code:`Request` objects too (the client should prepare these).

.. code:: python

    >>> request = twitterads.Request(resource='accounts')
    >>> client.send(request)
    <Twitter Response [OK]>

With both types of request, we don't want to validate the parameters on input. However, :code:`Request` objects should have the :code:`prepare` method implemented and it should ensure it's parameters are fit for sending.

.. code:: python

    >>> request = twitterads.Request(resource='campaigns')  # The campaigns resource requires an account ID. The client will fetch it when preparing the request.
    >>> client.send(request)
    <Twitter Response [OK]>

    >>> request = twitterads.PreparedRequest(resource='campaigns')  # The campaigns resource requires an account ID. However, since this request is already prepared, we don't fetch it.
    >>> client.send(request)
    <Twitter Response [Incomplete]>

We should be able to pass additional keyword arguments that make up the rest of the parameters in the request.

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='campaigns', account_id='abc123')
    >>> client.send(request)
    <Twitter Response [OK]>

The additional keyword arguments should be accepted in either the form of the API or in a Pythonic way.

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='accounts', with_deleted=True)
    >>> client.send(request)
    <Twitter Response [OK]>

    >>> request = twitterads.PreparedRequest(resource='accounts', with_deleted='true')
    >>> client.send(request)
    <Twitter Response [OK]>

If we pass an unknown resource, we should let Twitter respond with an error.

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='unknown_resource')
    >>> client.send(request)
    <Twitter Response [Incomplete]>

At a much higher level, I'd like to be able to get all my accounts with

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='unknown_resource')
    >>> client.get_accounts(with_deleted=True)
    <Twitter Response [OK]>

I'd like to get all my campaigns with

.. code:: python

    >>> request = twitterads.PreparedRequest(resource='unknown_resource')
    >>> client.get_campaigns(with_deleted=True)
    <Twitter Response [OK]>
