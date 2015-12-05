.. TwitterAds documentation master file, created by
   sphinx-quickstart on Sat Dec  5 15:18:22 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TwitterAds
==========

Welcome to TwitterAds; a Python wrapper around the Twitter Ads API.

The Twitter Ads API exposes a bunch of useful resources but interacting with 
each resource demands a certain familiarity with the API and the Twitter 
advertising platform. This package aims to ease these requirements where 
possible.

Getting started
---------------

Getting up and running is extremely easy. In short,

- Clone the repository
- Replace the credentials in `config.py` with your own
- Get some data

::

    >>> import twitter
    >>> twitter.get_accounts()
    <Twitter Response [OK]>

A more detailed guide follows:

.. toctree::
   :maxdepth: 1

   tutorial/usage_guide

Acknowledgements
----------------

This library wouldn't exist without **requests** whose model is the source of inspiration for the one you see here. Not only is the model a good one, the library is so wonderfully written that understanding it is simply a case of reading it.

