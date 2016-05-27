from twads import Client
import pytest
import json
import requests_mock


@pytest.fixture()
def client():
    return Client(
        consumer_key='foo', consumer_secret='foo', access_key='foo', access_secret='foo'
    )


@pytest.fixture(params=['single', 'multiple', 'bad_auth'])
def accounts(request):
    with open('tests/responses/accounts_{}.json'.format(request.param), 'r') as f:
        return json.load(f)


class TestGetAccounts:
    def test_get_accounts(self, client, accounts):
        try:
            expected_response = accounts['data']
        except KeyError:
            expected_response = accounts['errors']

        with requests_mock.mock() as m:
            m.get('https://ads-api.twitter.com/0/accounts', json=accounts)
            actual_response = client.get_accounts()

        assert expected_response == actual_response
