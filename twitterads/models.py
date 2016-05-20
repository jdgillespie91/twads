import time

import requests
from requests_oauthlib import OAuth1


class Request:
    def __init__(self, resource=None, **kwargs):
        self._resource = resource

    @property
    def resource(self):
        return self._resource


class PreparedRequest(object):
    """ A request, ready to be sent (in theory).

    A :class:`Request` object, once prepared, becomes a
    :class:`PreparedRequest` object. In theory, the prepared request should be
    appropriate for the Twitter Ads API. However, this validation happens on
    preparation of the :class:`Request` object as opposed to here so it's not
    necessarily the case.

    Do note that a :class:`PreparedRequest` object should be sent via a
    :class:`Client` object.

    :param resource: the resource to access.
    :type resource: str

    :Example:

        >>> request = twitterads.PreparedRequest(resource='accounts')
        >>> client.send(request)
        <Twitter Response [OK]>

        >>> request = twitter.PreparedRequest(
        ...     resource='accounts', with_deleted=False
        ... )
        >>> client.send(request)
        <Twitter Response [OK]>

    """
    def __init__(self, resource, **kwargs):
        self._resource = resource

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

    :param prepared_request: a prepared request.
    :type prepared_request: :class:`PreparedRequest`
    :return Response: a response object.

    """
    _base_endpoint = 'https://ads-api.twitter.com/0'
    _accounts_endpoint = _base_endpoint + '/accounts'
    _campaigns_endpoint = _accounts_endpoint + '/{0}/campaigns'
    _line_items_endpoint = _accounts_endpoint + '/{0}/line_items'

    def __init__(self):
        return
        self._request = prepared_request
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
                    sleep_for = max(
                        0, int(resp.headers['x-cost-rate-limit-reset']) - int(time.time())
                    )
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
        raise TypeError('Resource not recognised')

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

    def __init__(self, data=None, errors=None):
        self.data = data if data else []
        self.errors = errors if errors else []

    def __bool__(self):
        if not self.errors:
            return True
        return False

    def __repr__(self):
        if self:
            return '<Twitter Response [OK]>'
        return '<Twitter Response [Incomplete]>'

    def __add__(self, other):
        if not isinstance(other, Response):
            raise TypeError("Adding a non-Response to a Response is not supported")
        return Response(self.data + other.data, self.errors + other.errors)
