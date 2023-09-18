from datetime import datetime
from dateutil.parser import parse

import requests
import pytz


def localise_tz(naive_dt_string):
    """Converts a UTC datetime into a localised datetime defaulting to GMT.

    :param naive_dt_string: The naive datetime string to be converted
    :type naive_dt_string: str
    :return: The localised datetime string
    :rtype: str
    """

    # We only want to convert datetime not time
    try:
        naive_datetime = datetime.strptime(naive_dt_string, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return naive_dt_string

    tz = pytz.timezone("UTC")
    tz_time = tz.localize(naive_datetime)
    aware_datetime = tz_time.astimezone(tz=pytz.timezone("Europe/London"))

    return aware_datetime.isoformat()


def is_date(dt_string, fuzzy=False):
    """Return whether the :attr:`dt_string` can be interpreted as a date.

    :param dt_string: The string to check for datetime
    :type dt_string: str
    :param fuzzy: Ignore unknown tokens in :attr:`dt_string` if True
    :type fuzzy: bool
    :return: Whether the provided :attr:`dt_string` contains a datetime
    :rtype: bool
    """

    try:
        parse(dt_string, fuzzy=fuzzy)
        return True

    except (TypeError, ValueError):
        return False


def test_connection(api_url):
    """Tests that the Habitat API is operational and can connect.

    :param api_url: The URL of the Habitat API
    :type api_url: str
    :return: Result of the connection test
    :rtype: bool
    """

    try:
        resp = requests.get(f"{api_url}/environment/config")
        resp.raise_for_status()
        return True

    except Exception:
        return False
