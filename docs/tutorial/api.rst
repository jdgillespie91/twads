Using the API
=============

Let's call some of the functions exposed by the API module. 

Accounts
--------

First, let's get all accounts

::

    >>> accounts = twitter.get_accounts()
    >>> accounts
    <Twitter Response [OK]>

An :samp:`[OK]` response implies that we retrived all accounts successfully. We can see this is true by checking the :samp:`errors` attribute of :samp:`accounts`

::

    >>> accounts.errors
    []

You'll notice that if :samp:`get_accounts` is unsuccessful, the response object looks different. Let's force an unsuccessful response by passing something other than a boolean in as :samp:`with_deleted`

::

    >>> accounts = twitter.get_accounts(with_deleted='ops')
    >>> accounts
    <Twitter Response [Incomplete]>

Notice the difference? Checking :samp:`accounts.errors` reveals that Twitter was expecting us to pass a boolean to :samp:`with_deleted`

::

    >>> accounts.errors
    [{'errors': [{'parameter': 'with_deleted', 'message': 'Expected Boolean, got "ops" for with_deleted', 'code': 'INVALID_PARAMETER'}], 'request': {'params': {}}}]

Campaigns
---------

Of course, we can access other resources too.

::

    >>> campaigns = twitter.get_campaigns()
    >>> campaigns
    <Twitter Response [OK]>

That likely took a few seconds to complete. This is beacuse the :samp:`get_campaigns` function has to make many individual requests to the Twitter Ads API. Specifically, the API demands do separate requests per account and that we request at most 1000 campaigns at once.

To speed things up, we can request campaigns for specific accounts

::

    >>> accounts = twitter.get_accounts()
    >>> account_ids = [account['id'] for account in accounts.data[:3]]  # Get the first three account IDs only.
    >>> campaigns = twitter.get_campaigns(account_ids=account_ids)
    >>> campaigns
    <Twitter Response [OK]>

Note that we can choose whether to get deleted campaigns or not too.

::

    >>> len(campaigns.data)
    2742

    >>> live_campaigns = twitter.get_campaigns(account_ids=account_ids, with_deleted=False)
    >>> len(live_campaigns.data)
    2495

The :samp:`with_deleted` parameter applies at the level of the resource being requested. For higher-level entities, we'll always get all items. For example, in :samp:`get_campaigns`, we get campaigns whose status reflects the value of :samp:`with_deleted` but we consider all accounts (recall that in order to get campaigns, we must specify the account), deleted or otherwise.

Line Items
----------

We have a number of other entities available to us. One of these is line items and is called in exactly the same way as campaigns.

::

    >>> twitter.get_line_items(account_ids=account_ids)
    <Twitter Response [OK]>

Promoted tweets
---------------

Another of these entities is promoted tweets. Again, it is called in the same way as campaigns

::

    >>> twitter.get_promoted_tweets(account_ids=account_ids)
    <Twitter Response [OK]>

Stats
-----

The last available function is :samp:`get_stats`. A word of warning before using this function; as with the other requests listed here, this function sends multiple requests to the Twitter Ads API. Compartively though, this sends significantly more[#]_. Further, Twitter have put rate limiting in place against this resource so it's necessary to sleep at times. As such, it's definitely worth specifying :samp:`account_ids` initially and easing this constraint as you grow more comfortable with the function.

::

    >>> account_ids = [account['id'] for account in accounts.data[:1]] 
    >>> twitter.get_stats(account_ids=account_ids)
    <Twitter Response [OK]>

A final note is that stats are pulled at promoted tweet level only. In the future, you'll have more control over this.

That covers all functions available to you in the API. If you're more familiar with the Twitter Ads API and would like further tailor your requests, head :doc:`here <models>` to see how.

.. [#] The Twitter Ads API demands that you pull stats against at most 20 promoted tweets at a time.
