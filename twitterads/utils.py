from datetime import datetime

import pytz


def chunks(l, n):
    # TODO Write docstring and test against chunks (also rename it!).
    for i in range(0, len(l), n):
        yield l[i:i+n]


def encode_date(date_string, zone):
    """ Encodes date as per the requirements of the Twitter Ads API.

    This function accepts a date string and a timezone as arguments. The date
    string is converted to a string describing in UTC the time 00:00 on the
    date and in the timezone given. See the usage below for specific examples.

    :param date_string: str, describes date in format '%Y-%m-%d'
    :param zone: str, describes timezone (the string must exist in pytz.all_timezones)
    :return: string

    Usage::

        >>> encode_date('2015-01-01', 'UTC')
        '2015-01-01T00:00:00Z'
        >>> encode_date('2015-01-01', 'America/New_York')
        '2015-01-01T05:00:00Z'

    """
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    localized_dt = pytz.timezone(zone).localize(dt)
    utc_dt = localized_dt.astimezone(pytz.UTC)
    return utc_dt.replace(tzinfo=None).isoformat() + 'Z'
