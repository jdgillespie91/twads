from twads import Client
import pytest
import json
import requests_mock


@pytest.fixture()
def client():
    return Client(
        consumer_key='foo', consumer_secret='foo', access_key='foo', access_secret='foo'
    )


@pytest.fixture()
def accounts():
    with open('tests/accounts.json', 'r') as f:
        return json.load(f)


class TestMain:
    def test_get_accounts(self, client, accounts):
        expected_accounts = accounts['data']

        with requests_mock.mock() as m:
            m.get('https://ads-api.twitter.com/0/accounts', json=accounts)
            actual_accounts = client.get_accounts()

        assert expected_accounts == actual_accounts
