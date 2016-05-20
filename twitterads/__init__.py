""" TwitterAds

Welcome to TwitterAds; a Python wrapper around the Twitter Ads API.

The basic usage is as follows

    >>> import twitterads
    >>> client = twitterads.get_client(
    ...     client_key='...',
    ...     client_secret='...',
    ...     resource_owner_key='...',
    ...     resource_owner_secret='...'
    ... )
    >>> client.get_accounts()
    <Twitter Response [OK]>

More extensive documentation can be found at
http://twitter-ads-api.readthedocs.io/en/latest/

"""
from .api import get_client


__all__ = [
    'get_client'
]
