from datetime import date, timedelta

from .models import PreparedRequest, Response
from .utils import chunks, encode_date


def get_accounts(with_deleted=True):
    """ Get Twitter accounts.

    This method exposes the following endpoint:

    https://dev.twitter.com/ads/reference/get/accounts

    By default, we include deleted accounts.

    :param with_deleted: bool, True means that deleted accounts are included.
    :return: Response, a Twitter Response object.

    Usage::

        >>> import twitter
        >>> twitter.get_accounts()
        <Twitter Response [OK]>

    """
    optional_parameters = {'with_deleted': str(with_deleted).lower()}
    prepared_request = PreparedRequest('accounts',
                                       optional_parameters=optional_parameters)
    return prepared_request.send()


def get_campaigns(account_ids=None, with_deleted=True):
    """ Get Twitter campaigns.

    This method exposes the following endpoint:

    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/campaigns

    By default, we retrieve campaigns for all accounts and include deleted
    campaigns. Note that this can take a few minutes to complete.

    :param account_ids: list, a list of account IDs for which to get campaigns.
    :param with_deleted: bool, True means that deleted campaigns are included.
    :return: Response, a Twitter Response object.

    Usage::

        >>> import twitter
        >>> twitter.get_campaigns()  # This can take several minutes.
        <Twitter Response [OK]>

    """
    if not account_ids:
        accounts = get_accounts()
        account_ids = [account['id'] for account in accounts.data]

    response = Response()  # Instantiate empty Response so we have something to append to.
    for account_id in account_ids:
        required_parameters = {'account_id': account_id}
        optional_parameters = {'with_deleted': str(with_deleted).lower()}
        prepared_request = PreparedRequest(resource='campaigns',
                                           required_parameters=required_parameters,
                                           optional_parameters=optional_parameters)
        response += prepared_request.send()

    return response


def get_line_items(account_ids=None, with_deleted=True):
    """ Get Twitter line items.

    This method exposes the following endpoint:

    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/line_items

    By default, we retrieve campaigns for all accounts and include deleted
    line items. Note that this can take a few minutes to complete.

    :param account_ids: list, a list of account IDs for which to get line items.
    :param with_deleted: bool, True means that deleted line items are included.
    :return: Response, a Twitter Response object.

    Usage::

        >>> import twitter
        >>> twitter.get_line_items()  # This can take several minutes.
        <Twitter Response [OK]>

    """
    if not account_ids:
        accounts = get_accounts()
        account_ids = [account['id'] for account in accounts.data]

    response = Response()  # Instantiate empty Response so we have something to append to.
    for account_id in account_ids:
        required_parameters = {'account_id': account_id}
        optional_parameters = {'with_deleted': str(with_deleted).lower()}
        prepared_request = PreparedRequest(resource='line_items',
                                           required_parameters=required_parameters,
                                           optional_parameters=optional_parameters)
        response += prepared_request.send()

    return response


def get_promoted_tweets(account_ids=None, with_deleted=True):
    """ Get Twitter promoted tweets.

    This method exposes the following endpoint:

    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/promoted_tweets

    By default, we retrieve campaigns for all accounts and include deleted
    promoted tweets. Note that this can take a few minutes to complete.

    :param account_ids: list, a list of account IDs for which to get promoted tweets.
    :param with_deleted: bool, True means that deleted promoted tweets are included.
    :return: Response, a Twitter Response object.

    Usage::

        >>> import twitter
        >>> twitter.get_promoted_tweets()  # This can take several minutes.
        <Twitter Response [OK]>

    """
    if not account_ids:
        accounts = get_accounts()
        account_ids = [account['id'] for account in accounts.data]

    response = Response()  # Instantiate empty Response so we have something to append to.
    for account_id in account_ids:
        required_parameters = {'account_id': account_id}
        optional_parameters = {'with_deleted': str(with_deleted).lower()}
        prepared_request = PreparedRequest(resource='promoted_tweets',
                                           required_parameters=required_parameters,
                                           optional_parameters=optional_parameters)
        response += prepared_request.send()

    return response


def get_stats(account_ids=None, start_date=None, end_date=None):
    """ Get Twitter promoted tweets.

    This method exposes the following endpoint:

    https://dev.twitter.com/ads/reference/get/stats/accounts/%3Aaccount_id/promoted_tweets

    By default, we retrieve campaigns for all accounts and include deleted
    promoted tweets. Note that account IDs should ideally be passed. If not,
    this function can take hours to complete.

    :param account_ids: list, a list of account IDs for which to get promoted tweets.
    :param start_date: str, the start date in '%Y-%m-%d' format.
    :param end_date: str, the end date in '%Y-%m-%d' format.
    :return: Response, a Twitter Response object.

    Usage::

        >>> import twitter
        >>> twitter.get_stats(account_ids=['foo'])  # This can take several minutes.
        <Twitter Response [OK]>

    """
    accounts = get_accounts()  # Always get_accounts because we need the account timezone.
    if account_ids:
        accounts_data = [account for account in accounts.data if account['id'] in account_ids]
    else:
        accounts_data = accounts.data

    if not start_date:
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')

    if not end_date:
        end_date = date.today().strftime('%Y-%m-%d')

    response = Response()  # Instantiate empty Response so we have something to append to.
    for account in accounts_data:
        promoted_tweets = get_promoted_tweets(account_ids=[account['id']])
        promoted_tweet_ids = [promoted_tweet['id'] for promoted_tweet in promoted_tweets.data]
        for chunk in chunks(promoted_tweet_ids, 20):
            required_parameters = {'account_id': account['id'],
                                   'promoted_tweet_ids': ','.join(chunk),
                                   'start_time': encode_date(start_date, account['timezone'])}
            optional_parameters = {'granularity': 'DAY',
                                   'end_time': encode_date(end_date, account['timezone'])}
            prepared_request = PreparedRequest(resource='stats',
                                               required_parameters=required_parameters,
                                               optional_parameters=optional_parameters)
            response += prepared_request.send()

    return response


def get_tweets():
    pass
