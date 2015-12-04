import time

import requests
from requests_oauthlib import OAuth1

from structures import StringDescriptor, DictDescriptor, ListDescriptor
from config import CONFIG


class PreparedRequest(object):
    """ A '<Twitter Prepared Request [resource]>' object.

    The '<Twitter Prepared Request [resource]>' object is used to send a
    request to one of the Twitter APIs (the API called will depend on the
    resource requested).

    The following resources are available:

    account
    https://dev.twitter.com/ads/reference/get/accounts

    campaigns
    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/campaigns

    line_items
    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/line_items

    promoted_tweets
    https://dev.twitter.com/ads/reference/get/accounts/%3Aaccount_id/promoted_tweets

    stats
    https://dev.twitter.com/ads/reference/get/stats/accounts/%3Aaccount_id/promoted_tweets

    The documentation covers in great detail the required and optional
    parameters. Simply pass these along with your resource to customise your
    response. There are examples of this below.

    :param resource: str, the resource to access.
    :param required_parameters: dict, the parameters required by the resource.
    :param optional_parameters: dict, the optional parameters for the resource.

    Usage::

        >>> import infrastructure.apis import twitter
        >>> request = twitter.PreparedRequest(resource='accounts')
        >>> request.send()
        <Twitter Response [Complete]>

        >>> request = twitter.PreparedRequest(resource='campaigns',
                                              required_parameters={'account_id': 'xxx'},
                                              optional_parameters={'with_deleted': 'false'})
        >>> request.send()
        <Twitter Response [Complete]>

    """
    # TODO Go through the docstrings, run the associated code and ensure the output is
    # accurate.
    # TODO Make a note to move resource documentation and endpoint selection to the same
    # class! Either here or the Adapter, but not both.
    resource = StringDescriptor()
    api = StringDescriptor()
    required_parameters = DictDescriptor()
    optional_parameters = DictDescriptor()

    def __init__(self, resource, required_parameters=None, optional_parameters=None):
        self.resource = resource
        self.api = 'Ads API'  # Until I expose other APIs, I'll hardcode this value.
        self.required_parameters = required_parameters if required_parameters else {}
        self.optional_parameters = optional_parameters if optional_parameters else {}

    def send(self):
        adapter = Adapter(self)
        return adapter.send()

    def __repr__(self):
        return '<Twitter Prepared Request [{0}]>'.format(self.resource)


class Adapter(object):
    """ A '<Twitter Adapter [Ads API]>' object.

    The '<Twitter Adapter [Ads API]>' object is used to make the requests to
    the Twitter Ads API. It is instantiated with a single PreparedRequest
    instance and hence is hitting a single endpoint with the same set of
    parameters.

    The adapter object is responsible for two things; pagination and retrying.
    Pagination refers to the fact that the Ads API limits the amount of data
    returned in a single GET and so it can require multiple hits to the same
    endpoint to gather all the requested data. The page requested is
    determined by the cursor attribute of the params dictionary and is handled
    here by the send() method.

    Retrying refers to the fact that in some instances, the API may return a
    response that implies that the request, although unsuccessful, is not
    fundamentally wrong. In such instances, it may be appropriate to retry.
    The retry logic is handled here by the _retry_request() method.

    :param prepared_request: PreparedRequest, a prepared request object.
    :return Response: a response object.

    """
    # TODO Go through the docstrings, run the associated code and ensure the output is
    # accurate.
    # TODO Find a way of declaring the endpoints in a more concise and extendable fashion.
    # If I have to implement each endpoint individually, it should at least be extremely
    # easy to do this.
    # TODO Decide what to put in the errors list. Do this by hitting a bunch of requests,
    # getting some errors and thinking about what would be useful if you were to required
    # to debug that error.
    _base_endpoint = 'https://ads-api.twitter.com/0'
    _accounts_endpoint = _base_endpoint + '/accounts'
    _campaigns_endpoint = _accounts_endpoint + '/{0}/campaigns'
    _line_items_endpoint = _accounts_endpoint + '/{0}/line_items'
    _promoted_tweets_endpoint = _accounts_endpoint + '/{0}/promoted_tweets'
    _stats_endpoint = _base_endpoint + '/stats/accounts/{0}/promoted_tweets'

    def __init__(self, prepared_request):
        # Used to determine url and parameters to request.
        self._request = prepared_request

        # Used to store the data returned by send.
        self._data = []
        self._errors = []

    def send(self):
        resp = self._retry_request()
        while True:
            resp_json = resp.json()
            if resp.status_code == 200:
                self._data.extend(resp_json['data'])
                if resp_json.get('next_cursor', False):
                    self.params['cursor'] = resp_json['next_cursor']
                    resp = self._retry_request()
                    continue
            else:
                self._errors.append(resp_json)
            break
        return Response(self._data, self._errors)

    def _retry_request(self):
        retry_codes = [429]
        max_tries = 3
        tries = 0
        resp = None

        while True:
            resp = requests.get(url=self.endpoint, params=self.params, auth=self.auth)
            if resp.status_code in retry_codes and tries < max_tries:
                # 429 is RATE_LIMIT_EXCEEDED. In the response header, Twitter provides the
                # time at which our rate limit will reset (at most, 15 minutes). We sleep
                # until then.
                if resp.status_code == 429:
                    sleep_for = max(0, int(resp.headers['x-cost-rate-limit-reset']) - int(time.time()))
                    print('Sleeping for {0} seconds'.format(sleep_for))
                    time.sleep(sleep_for)

                tries += 1
                continue
            break
        return resp

    @property
    def auth(self):
        return OAuth1(client_key=CONFIG['CONSUMER_KEY'],
                      client_secret=CONFIG['CONSUMER_SECRET'],
                      resource_owner_key=CONFIG['ACCESS_KEY'],
                      resource_owner_secret=CONFIG['ACCESS_SECRET'])

    @property
    def request(self):
        return self._request

    @property
    def endpoint(self):
        if self.request.resource == 'accounts':
            return self._accounts_endpoint
        elif self.request.resource == 'campaigns':
            return self._campaigns_endpoint.format(
                self.request.required_parameters['account_id'])
        elif self.request.resource == 'line_items':
            return self._line_items_endpoint.format(
                self.request.required_parameters['account_id'])
        elif self.request.resource == 'promoted_tweets':
            return self._promoted_tweets_endpoint.format(
                self.request.required_parameters['account_id'])
        elif self.request.resource == 'stats':
            return self._stats_endpoint.format(
                self.request.required_parameters['account_id'])
        raise TypeError('Resource not recognised')

    @property
    def params(self):
        # If the resource requested is stats, some required parameters need to be passed
        # along with the optional parameters.
        if self.request.resource == 'stats':
            self.request.optional_parameters['promoted_tweet_ids'] = self.request.required_parameters['promoted_tweet_ids']
            self.request.optional_parameters['start_time'] = self.request.required_parameters['start_time']
        return self.request.optional_parameters

    def __repr__(self):
        return '<Twitter Adapter [Ads API]>'


class Response(object):
    """ A '<Twitter Response [status]>' object.

    The '<Twitter Response [status]>' object is a carrier of information
    returned by the adapter. It should only need to be instantiated by the
    adapter.

    The object contains three attributes; data, errors and ok. The first is a
    list of entities returned by the adapter. The second is a list of failed
    requests returned while gathering the entities. The third is a boolean
    that reflects the success of the requests.

    :param data: list, the entities provided by the resource.
    :param errors: dict, any failed requests whilist gathering the resource
    entities.

    """
    # TODO Go through the docstrings, run the associated code and ensure the output is
    # accurate.
    data = ListDescriptor()
    errors = ListDescriptor()

    def __init__(self, data=None, errors=None):
        self.data = data if data else []
        self.errors = errors if errors else []

    @property
    def ok(self):
        if not self.errors:
            return True
        return False

    def __bool__(self):
        return self.ok

    def __repr__(self):
        if self.ok:
            return '<Twitter Response [OK]>'
        return '<Twitter Response [Incomplete]>'

    def __add__(self, other):
        if not isinstance(other, Response):
            raise TypeError("Adding a non-Response to a Response is not supported")
        return Response(self.data + other.data, self.errors + other.errors)
