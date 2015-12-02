import unittest

from utils import encode_date


class EncodeDateTests(unittest.TestCase):
    def test_encode_date_works_correctly(self):
        actual = encode_date('2015-01-01', 'UTC')
        expected = '2015-01-01T00:00:00Z'
        self.assertEquals(expected, actual)

        actual = encode_date('2015-01-01', 'Europe/London')
        expected = '2015-01-01T00:00:00Z'
        self.assertEquals(expected, actual)

        actual = encode_date('2015-01-01', 'America/New_York')
        expected = '2015-01-01T05:00:00Z'
        self.assertEquals(expected, actual)

        actual = encode_date('2015-01-01', 'Asia/Tokyo')
        expected = '2014-12-31T15:00:00Z'
        self.assertEquals(expected, actual)

        # Test some dates that are impacted by daylight savings.
        actual = encode_date('2015-10-20', 'Europe/London')
        expected = '2015-10-19T23:00:00Z'
        self.assertEquals(expected, actual)

        actual = encode_date('2015-10-30', 'America/New_York')
        expected = '2015-10-30T04:00:00Z'
        self.assertEquals(expected, actual)


if __name__ == "__main__":
    test_cases = [EncodeDateTests]

    for test_case in test_cases:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)


