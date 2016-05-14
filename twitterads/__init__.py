# TODO Include link to docs below
""" TwitterAds

Welcome to TwitterAds; a Python wrapper around the Twitter Ads API.

The basic usage is as follows

    >>> import twitter
    >>> accounts = twitter.get_accounts()
    >>> accounts
    <Twitter Response [OK]>

More extensive documentation can be found at ...

"""
from .api import get_accounts, get_campaigns, get_line_items, get_promoted_tweets, \
    get_tweets, get_stats
from .models import PreparedRequest


__all__ = [
    'get_accounts',
    'get_campaigns',
    'get_line_items',
    'get_promoted_tweets',
    'get_tweets',
    'get_stats',
    'PreparedRequest'
]
