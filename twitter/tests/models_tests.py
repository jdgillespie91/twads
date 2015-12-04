import time
import unittest

import requests
from models import PreparedRequest, Adapter, Response
from mock import Mock, MagicMock, patch
from requests_oauthlib import OAuth1


class RequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.foo_string = 'foo'
        cls.foo_dict = {'foo': 'foo'}
        cls.foo_list = ['foo']

    def test_request_requires_resource_to_be_passed_when_instantiating(self):
        with self.assertRaises(TypeError):
            PreparedRequest()
        PreparedRequest(resource=self.foo_string)

    def test_request_has_necessary_attributes(self):
        request = PreparedRequest(resource='foo')
        self.assertTrue(hasattr(request, 'resource'))
        self.assertTrue(hasattr(request, 'required_parameters'))
        self.assertTrue(hasattr(request, 'optional_parameters'))
        self.assertTrue(hasattr(request, 'send'))

    def test_request_assigns_attributes_correctly_on_instantiation(self):
        request = PreparedRequest(resource=self.foo_string, required_parameters=self.foo_dict,
                                  optional_parameters=self.foo_dict)

        self.assertEquals(self.foo_string, request.resource)
        self.assertEquals(self.foo_dict, request.required_parameters)
        self.assertEquals(self.foo_dict, request.optional_parameters)

    def test_request_assigns_attributes_correctly_after_instantiation(self):
        request = PreparedRequest(resource='bar')

        request.resource = self.foo_string
        self.assertEquals(self.foo_string, request.resource)

        request.required_parameters = self.foo_dict
        self.assertEquals(self.foo_dict, request.required_parameters)

        request.optional_parameters = self.foo_dict
        self.assertEquals(self.foo_dict, request.optional_parameters)

    def test_request_raises_type_error_if_arguments_are_wrong_type(self):
        for non_string in [1, [1], {1}, {'1': 1}, (1, 1)]:
            with self.assertRaises(TypeError):
                PreparedRequest(resource=non_string)

            request = PreparedRequest(resource='foo')
            with self.assertRaises(TypeError):
                request.resource = non_string

        for non_dict in [1, [1], {1}, '1', (1, 1)]:
            with self.assertRaises(TypeError):
                PreparedRequest(resource='str', required_parameters=non_dict)

            with self.assertRaises(TypeError):
                PreparedRequest(resource='str', optional_parameters=non_dict)

            request = PreparedRequest(resource='foo', required_parameters=self.foo_dict)
            with self.assertRaises(TypeError):
                request.required_parameters = non_dict

            request = PreparedRequest(resource='foo', optional_parameters=self.foo_dict)
            with self.assertRaises(TypeError):
                request.optional_parameters = non_dict

    def test_send_method_calls_adapter_send_method(self):
        with patch.object(PreparedRequest, 'send', return_value=None) as request_send:
            request = PreparedRequest(resource=self.foo_string)
            request.send()
        request_send.assert_called_once()

    def test_send_method_returns_response_object(self):
        with patch.object(Adapter, 'send', return_value=Response()) as adapter_send:
            request = PreparedRequest(resource=self.foo_string)
            response = request.send()
        self.assertIsInstance(response, Response)

    def test_repr_outputs_as_intended(self):
        request = PreparedRequest(resource=self.foo_string)
        self.assertEquals('<Twitter Prepared Request [foo]>', repr(request))

        request = PreparedRequest(resource='bar')
        self.assertEquals('<Twitter Prepared Request [bar]>', repr(request))

    def test_parameters_default_to_empty_dict(self):
        request = PreparedRequest(resource=self.foo_string)
        self.assertEquals({}, request.required_parameters)
        self.assertEquals({}, request.optional_parameters)

        # Ensure that the dictionary used is different across different instances of
        # PreparedRequest.
        another_request = PreparedRequest(resource=self.foo_string)
        self.assertNotEqual(id(request.optional_parameters),
                            id(another_request.optional_parameters))
        self.assertNotEqual(id(request.required_parameters),
                            id(another_request.required_parameters))


class AdapterTests(unittest.TestCase):
    def setUp(self):
        # We mock the Request class so that, if Request changes, we have an
        # obvious starting point from which to make changes to the Adapter
        # class.
        request = Mock()
        request.resource = 'accounts'
        request.api = 'Ads API'
        request.required_parameters = {}
        request.optional_parameters = {}
        self.accounts_adapter = Adapter(prepared_request=request)

    def test_adapter_requires_request_to_be_passed_when_instantiating(self):
        with self.assertRaises(TypeError):
            Adapter()

    def test_request_has_necessary_attributes(self):
        self.assertTrue(hasattr(self.accounts_adapter, 'auth'))
        self.assertTrue(hasattr(self.accounts_adapter, 'request'))
        self.assertTrue(hasattr(self.accounts_adapter, 'endpoint'))
        self.assertTrue(hasattr(self.accounts_adapter, 'params'))
        self.assertTrue(hasattr(self.accounts_adapter, 'send'))

    def test_auth_attribute_is_oauth1_object(self):
        self.assertIsInstance(self.accounts_adapter.auth, OAuth1)

    def test_endpoint_attribute_returns_str(self):
        self.assertIsInstance(self.accounts_adapter.endpoint, str)

    def test_endpoint_contains_twitter_base_endpoint(self):
        self.assertIn(Adapter._base_endpoint, self.accounts_adapter.endpoint)

    def test_endpoint_is_built_correctly_for_accounts(self):
        self.assertEquals(Adapter._accounts_endpoint, self.accounts_adapter.endpoint)

    def test_endpoints_are_built_correctly_for_other_entities(self):
        # 'Other' includes campaigns, line_items and promoted_tweets.
        request = MagicMock()
        account = 'acc_a'
        request.required_parameters = {'account_id': account}

        request.resource = 'campaigns'
        adapter = Adapter(prepared_request=request)
        self.assertEquals(Adapter._campaigns_endpoint.format(account), adapter.endpoint)

        request.resource = 'line_items'
        adapter = Adapter(prepared_request=request)
        self.assertEquals(Adapter._line_items_endpoint.format(account), adapter.endpoint)

        request.resource = 'promoted_tweets'
        adapter = Adapter(prepared_request=request)
        self.assertEquals(Adapter._promoted_tweets_endpoint.format(account), adapter.endpoint)

    def test_endpoints_and_parameters_are_built_correctly_for_stats_entities(self):
        # Stats is only available at promoted_tweet level currently.
        request = MagicMock()
        account = 'acc_a'
        promoted_tweets = 'pt_a,pt_b'
        start_time = '2015-01-01T00:00:00Z'
        request.required_parameters = {'account_id': account,
                                       'promoted_tweet_ids': promoted_tweets,
                                       'start_time': start_time}
        request.optional_parameters = {}

        request.resource = 'stats'
        adapter = Adapter(prepared_request=request)
        self.assertEquals(Adapter._stats_endpoint.format(account), adapter.endpoint)
        self.assertEquals({'promoted_tweet_ids': promoted_tweets,
                           'start_time': start_time},
                          adapter.params)

    def test_unknown_resource_raises_type_error_when_getting_endpoint(self):
        request = MagicMock()
        request.resource = 'unknown'
        adapter = Adapter(prepared_request=request)
        with self.assertRaises(TypeError):
            adapter.endpoint

    def test_params_returns_empty_dictionary_if_no_optional_params_in_request(self):
        self.assertEquals({}, self.accounts_adapter.params)

    def test_params_returns_optional_params_if_in_request(self):
        request = Mock()
        request.resource = 'accounts'
        request.optional_parameters = {'with_deleted': 'false'}
        adapter = Adapter(prepared_request=request)
        self.assertEquals(request.optional_parameters, adapter.params)

    def test_send_calls_retry_request(self):
        resp = MagicMock()
        resp.json = Mock()
        resp.status_code = Mock()
        with patch.object(Adapter, '_retry_request', return_value=resp) as retry_request:
            self.accounts_adapter.send()

        retry_request.assert_any_call()

    def test_send_retries_and_assigns_cursor_if_next_cursor_is_returned_once(self):
        # We assume the response returns data and next cursor on the first call and data
        # only on the second call.
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(side_effect=[{'data': 'foo', 'next_cursor': 'foo'},
                                           {'data': 'foo'}])
        with patch.object(Adapter, '_retry_request', return_value=resp) as retry_request:
            self.accounts_adapter.send()

        self.assertEquals(2, retry_request.call_count)
        self.assertEquals('foo', self.accounts_adapter.params['cursor'])

    def test_send_retries_and_assigns_cursor_if_next_cursor_is_returned_twice(self):
        # We assume the response returns data and next cursor on the first and second calls
        # and data only on the third.
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(side_effect=[{'data': 'foo', 'next_cursor': 'foo'},
                                           {'data': 'foo', 'next_cursor': 'bar'},
                                           {'data': 'foo'}])
        with patch.object(Adapter, '_retry_request', return_value=resp) as retry_request:
            self.accounts_adapter.send()

        self.assertEquals(3, retry_request.call_count)
        self.assertEquals('bar', self.accounts_adapter.params['cursor'])

    def test_send_returns_response_with_data_retrieved_when_no_next_cursor(self):
        data = [{'id': 'foo'}]
        resp = {'data': data}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json = MagicMock(side_effect=[resp])
        with patch.object(Adapter, '_retry_request', return_value=mock_resp):
            response = self.accounts_adapter.send()

        self.assertIsInstance(response, Response)
        self.assertEquals(data, response.data)
        self.assertEquals([], response.errors)

    def test_send_returns_response_with_data_retrieved_when_one_next_cursor(self):
        data = [{'id': 'foo'}]
        resp = {'data': data}
        resp_with_next_cursor = {'data': data, 'next_cursor': 'foo'}

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json = MagicMock(side_effect=[resp_with_next_cursor, resp])
        with patch.object(Adapter, '_retry_request', return_value=mock_resp):
            response = self.accounts_adapter.send()

        self.assertIsInstance(response, Response)
        self.assertEquals(data + data, response.data)
        self.assertEquals([], response.errors)

    def test_send_returns_response_with_errors_if_errors(self):
        errors = [{'code': 'foo'}]
        request = {'params': 'bar'}
        resp = {'errors': errors, 'request': request}

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.json = MagicMock(side_effect=[resp])
        with patch.object(Adapter, '_retry_request', return_value=mock_resp):
            response = self.accounts_adapter.send()

        self.assertIsInstance(response, Response)
        self.assertEquals([resp], response.errors)
        self.assertEquals([], response.data)

    def test_retry_request_calls_requests_get(self):
        requests.get = Mock()
        self.accounts_adapter._retry_request()
        self.assertGreater(requests.get.call_count, 0)

    @patch('requests.get')
    @patch('time.time')
    @patch('time.sleep')
    def test_retry_request_calls_requests_get_correct_number_of_times(self, mock_sleep, mock_time, mock_get):
        resp = Mock()
        resp.status_code = 429  # This value needs to be in retry_codes as defined in _retry_request.
        resp.headers = {'x-cost-rate-limit-reset': 0}
        mock_get.return_value = resp
        self.accounts_adapter._retry_request()
        self.assertEquals(mock_get.call_count, 4)  # This value needs to be one greater than max_tries as defined in _retry_request.

    @patch('requests.get')
    def test_retry_request_only_retries_for_correct_status_code(self, mock_get):
        resp = Mock()
        resp.status_code = 0  # Not a real status code so shouldn't ever retry for it.
        mock_get.return_value = resp
        self.accounts_adapter._retry_request()
        self.assertEquals(requests.get.call_count, 1)

    @patch('requests.get')
    @patch('time.time')
    @patch('time.sleep')
    def test_retry_request_sleeps_for_correct_amount_of_time_if_api_returns_429(self, mock_sleep, mock_time, mock_get):
        """ If the API returns a 429, we should sleep until the rate limit is reset. """
        now_time = int(time.time())
        mock_time.return_value = now_time
        reset_times = [now_time + 10, now_time + 20]  # Test two different times to prevent hard-coding one.

        for reset_time in reset_times:
            resp = Mock()
            resp.status_code = 429
            resp.headers = {'x-cost-rate-limit-reset': reset_time}
            mock_get.return_value = resp
            self.accounts_adapter._retry_request()
            self.assertGreater(mock_sleep.call_count, 0)
            mock_sleep.assert_called_with(reset_time - now_time)

    @patch('requests.get')
    @patch('time.time')
    @patch('time.sleep')
    def test_retry_request_never_sleeps_for_negative_time(self, mock_sleep, mock_time, mock_get):
        """ If the API returns a 429, we should sleep until the rate limit is reset. """
        now_time = int(time.time())
        mock_time.return_value = now_time
        reset_time = now_time - 10

        resp = Mock()
        resp.status_code = 429
        resp.headers = {'x-cost-rate-limit-reset': reset_time}
        mock_get.return_value = resp
        self.accounts_adapter._retry_request()
        mock_sleep.assert_called_with(0)

    @patch('requests.get')
    def test_retry_request_returns_resp(self, mock_get):
        resp = Mock()
        resp.status_code = 0  # Not a real status code so shouldn't ever retry for it.
        mock_get.return_value = resp

        self.assertEquals(resp, self.accounts_adapter._retry_request())

    def test_repr_outputs_as_intended(self):
        self.assertEquals('<Twitter Adapter [Ads API]>', repr(self.accounts_adapter))


class ResponseTests(unittest.TestCase):
    def test_response_can_be_instantiated_with_no_arguments(self):
        Response()

    def test_response_has_necessary_attributes(self):
        response = Response()
        self.assertTrue(hasattr(response, 'data'))
        self.assertTrue(hasattr(response, 'errors'))
        self.assertTrue(hasattr(response, 'ok'))

    def test_response_can_be_instantiated_with_data_only(self):
        Response(data=None)
        Response(data=[])
        Response(data=[1])

    def test_response_can_be_instantiated_with_errors_only(self):
        Response(errors=None)
        Response(errors=[])
        Response(errors=[1])

    def test_response_raises_if_instantiated_with_non_lists(self):
        for non_list in [1, '1', {1}, {'1': 1}, (1, 1)]:
            with self.assertRaises(TypeError):
                Response(data=non_list)
            with self.assertRaises(TypeError):
                Response(errors=non_list)

    def test_data_is_assigned_to_attribute_if_not_none(self):
        data = [1, 2, 3]
        response = Response(data=data)
        self.assertEquals(data, response.data)

    def test_data_attribute_is_empty_list_if_data_is_none(self):
        self.assertEquals([], Response().data)

    def test_errors_is_assigned_to_attribute_if_not_none(self):
        errors = [4, 5, 6]
        response = Response(errors=errors)
        self.assertEquals(errors, response.errors)

    def test_errors_attribute_is_empty_list_if_errors_is_none(self):
        self.assertEquals([], Response().errors)

    def test_ok_returns_true_if_errors_is_empty(self):
        response = Response(data=[1, 2, 3], errors=None)
        self.assertTrue(response.ok)

        response = Response(data=None, errors=None)
        self.assertTrue(response.ok)

    def test_ok_returns_false_if_errors_not_empty(self):
        response = Response(data=[1, 2, 3], errors=[1, 2, 3])
        self.assertFalse(response.ok)

        response = Response(data=None, errors=[1, 2, 3])
        self.assertFalse(response.ok)

    def test_bool_returns_true_if_errors_is_empty(self):
        response = Response(data=[1, 2, 3], errors=None)
        self.assertTrue(response)

        response = Response(data=None, errors=None)
        self.assertTrue(response)

    def test_bool_returns_false_if_errors_not_empty(self):
        response = Response(data=[1, 2, 3], errors=[1, 2, 3])
        self.assertFalse(response)

        response = Response(data=None, errors=[1, 2, 3])
        self.assertFalse(response)

    def test_empty_response_is_added_to_non_empty_response_correctly(self):
        data_a = [1]
        errors_a = ['a']
        response_a = Response(data=data_a, errors=errors_a)
        response_b = Response()

        response_sum = response_a + response_b
        self.assertEquals(data_a, response_sum.data)
        self.assertEquals(errors_a, response_sum.errors)

    def test_non_empty_responses_are_added_correctly(self):
        data_a = [1]
        errors_a = ['a']
        response_a = Response(data=data_a, errors=errors_a)

        data_b = [2]
        errors_b = ['b']
        response_b = Response(data=data_b, errors=errors_b)

        response_sum = response_a + response_b
        self.assertEquals(data_a + data_b, response_sum.data)
        self.assertEquals(errors_a + errors_b, response_sum.errors)

    def test_adding_non_response_to_response_raises_type_error(self):
        response = Response()
        for non_response in [1, '1', {1}, {'1': 1}, (1, 1), [1]]:
            with self.assertRaises(TypeError):
                response + non_response

    def test_repr_outputs_as_intended(self):
        response = Response(data=[1])
        self.assertEquals('<Twitter Response [OK]>', repr(response))

        response = Response(errors=[1])
        self.assertEquals('<Twitter Response [Incomplete]>', repr(response))


if __name__ == "__main__":
    test_cases = [RequestTests, AdapterTests, ResponseTests]

    for test_case in test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
