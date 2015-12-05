Installation
============

First, let's install the library. The required steps are as follows:

- Clone the `repository <https://dev.twitter.com/ads/overview/obtaining-ads-account-access>`_.
- Install the required modules with

::

    pip install -r requirements.txt

- Replace the dictionary keys in :samp:`config.py` with your credentials. See 
  `this page <https://dev.twitter.com/ads/overview/obtaining-ads-account-access>`_
  for more information on obtaining these credentials.
- With the project directory in your :envvar:`PYTHONPATH` variable, open up a 
  console and run

::

    >>> import twitter
    >>> twitter.get_accounts()
    <Twitter Response [OK]>

If you see the above output, you're all set. Head :doc:`here <api>` to start using the API.

Common issues
_____________

If, instead of the above, you see

::

    >>> twitter.get_accounts()
    <Twitter Response [Incomplete]>

then you are likely unauthorized. For further detail on the issue, run

::

    >>> accounts = twitter.get_accounts()
    >>> accounts.errors
    [{'errors': [{'message': 'This request is not properly authenticated', 'code': 'UNAUTHORIZED_ACCESS'}], 'request': {'params': {}}}]

