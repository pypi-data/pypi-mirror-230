import pytest

from climix.index_functions import support
from datetime import datetime


TEST_PARSE_ISODATE_PARAMETERS = [
    ("1961", datetime(1961, 1, 1)),
    ("2050", datetime(2050, 1, 1)),
    ("2010-01", datetime(2010, 1, 1)),
    ("2010-07", datetime(2010, 7, 1)),
    ("2010-01-01", datetime(2010, 1, 1)),
    ("2010-07-26", datetime(2010, 7, 26)),
]


@pytest.mark.parametrize("date, expected", TEST_PARSE_ISODATE_PARAMETERS)
def test_parse_isodate(date, expected):
    """Test ``test_parse_isodate``."""
    assert support.parse_isodate(date) == expected


TEST_PARSE_ISODATE_UPPER_BOUND_PARAMETERS = [
    ("1961", datetime(1962, 1, 1)),
    ("2050", datetime(2051, 1, 1)),
    ("2010-01", datetime(2010, 2, 1)),
    ("2010-07", datetime(2010, 8, 1)),
    ("2010-01-01", datetime(2010, 1, 2)),
    ("2010-07-26", datetime(2010, 7, 27)),
]


@pytest.mark.parametrize("date, expected", TEST_PARSE_ISODATE_UPPER_BOUND_PARAMETERS)
def test_parse_isodate_upper_bound(date, expected):
    """Test ``test_parse_isodate_upper_bound``."""
    assert support.parse_isodate_upper_bound(date) == expected


TEST_PARSE_ISODATE_TIMERANGE_PARAMETERS = [
    ("1961/1990", support.TimeRange(datetime(1961, 1, 1), datetime(1991, 1, 1), False)),
    ("2010/2050", support.TimeRange(datetime(2010, 1, 1), datetime(2051, 1, 1), False)),
    (
        "1961-01/2050-01",
        support.TimeRange(datetime(1961, 1, 1), datetime(2050, 2, 1), False),
    ),
    (
        "1961-01/2050-01",
        support.TimeRange(datetime(1961, 1, 1), datetime(2050, 2, 1), False),
    ),
    (
        "1961-01/2050-01",
        support.TimeRange(datetime(1961, 1, 1), datetime(2050, 2, 1), False),
    ),
    ("P20Y/1990", support.TimeRange(datetime(1971, 1, 1), datetime(1991, 1, 1), False)),
    ("1961/P20Y", support.TimeRange(datetime(1961, 1, 1), datetime(1981, 1, 1), False)),
    (
        "P20Y6M/1990",
        support.TimeRange(datetime(1970, 7, 1), datetime(1991, 1, 1), False),
    ),
    (
        "1961/P20Y6M",
        support.TimeRange(datetime(1961, 1, 1), datetime(1981, 7, 1), False),
    ),
]


@pytest.mark.parametrize("timerange, expected", TEST_PARSE_ISODATE_TIMERANGE_PARAMETERS)
def test_parse_isodate_timerange(timerange, expected):
    """Test ``test_parse_isodate_timerange``."""
    assert support.parse_isodate_timerange(timerange) == expected
