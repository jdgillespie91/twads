from unittest.mock import Mock

import pytest

from twitterads.client import Client
from twitterads.models import Response, Adapter


@pytest.fixture
def client():
    return Client()


class TestClient:
    def test_get_accounts(self, client):
        client.send = Mock()

        client.get_accounts()

        args = client.send.call_args[0]
        request = args[0]
        assert request.resource == 'accounts'

    def test_get_campaigns(self, client):
        client.send = Mock()

        client.get_accounts()

        args = client.send.call_args[0]
        request = args[0]
        assert request.resource == 'accounts'

    def test_send(self, client):
        response = client.send('foo')
        assert isinstance(response, Response)

    def test_adapter(self, client):
        assert isinstance(client._adapter, Adapter)
