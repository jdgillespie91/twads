from twitterads.api import get_client
from twitterads.client import Client


class TestGetClient:
    def test_get_client_returns_client_object(self):
        actual_client = get_client(
            client_key='foo',
            client_secret='foo',
            resource_owner_key='foo',
            resource_owner_secret='foo',
        )
        assert isinstance(actual_client, Client)
