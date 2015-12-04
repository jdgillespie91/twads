import unittest

from mock import patch

from ..api import get_accounts, get_campaigns, get_line_items, get_promoted_tweets, get_stats
from ..models import Response


class GetAccountsTests(unittest.TestCase):
    @patch('models.Adapter.send')
    def test_get_accounts_returns_response_object(self, mock_send):
        mock_send.return_value = Response()
        accounts = get_accounts()
        self.assertIsInstance(accounts, Response)


class GetCampaignsTests(unittest.TestCase):
    @patch('models.Adapter.send')
    def test_get_campaigns_returns_response_object(self, mock_send):
        mock_send.return_value = Response()
        campaigns = get_campaigns()
        self.assertIsInstance(campaigns, Response)

    @patch('api.get_accounts')
    def test_get_accounts_is_called_correctly(self, mock_get_accounts):
        get_campaigns()
        self.assertEquals(1, mock_get_accounts.call_count)
        get_campaigns(account_ids=['acc_a'])
        self.assertEquals(1, mock_get_accounts.call_count)


class GetLineItemsTests(unittest.TestCase):
    @patch('models.Adapter.send')
    def test_get_campaigns_returns_response_object(self, mock_send):
        mock_send.return_value = Response()
        line_items = get_line_items()
        self.assertIsInstance(line_items, Response)

    @patch('api.get_accounts')
    def test_get_accounts_is_called_correctly(self, mock_get_accounts):
        get_line_items()
        self.assertEquals(1, mock_get_accounts.call_count)
        get_line_items(account_ids=['acc_a'])
        self.assertEquals(1, mock_get_accounts.call_count)


class GetPromotedTweetsTests(unittest.TestCase):
    @patch('models.Adapter.send')
    def test_get_campaigns_returns_response_object(self, mock_send):
        mock_send.return_value = Response()
        promoted_tweets = get_promoted_tweets()
        self.assertIsInstance(promoted_tweets, Response)

    @patch('api.get_accounts')
    def test_get_accounts_is_called_correctly(self, mock_get_accounts):
        get_promoted_tweets()
        self.assertEquals(1, mock_get_accounts.call_count)
        get_promoted_tweets(account_ids=['acc_a'])
        self.assertEquals(1, mock_get_accounts.call_count)


class GetStatsTests(unittest.TestCase):
    @patch('models.Adapter.send')
    def test_get_campaigns_returns_response_object(self, mock_send):
        mock_send.return_value = Response()
        stats = get_stats()
        self.assertIsInstance(stats, Response)

    @patch('api.get_accounts')
    def test_get_accounts_is_called_correctly(self, mock_get_accounts):
        get_promoted_tweets()
        self.assertEquals(1, mock_get_accounts.call_count)
        get_promoted_tweets(account_ids=['acc_a'])
        self.assertEquals(2, mock_get_accounts.call_count)


class GetTweetsTests(unittest.TestCase):
    pass


if __name__ == "__main__":
    test_cases = [GetAccountsTests, GetCampaignsTests, GetLineItemsTests,
                  GetPromotedTweetsTests, GetStatsTests, GetTweetsTests]

    for test_case in test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
