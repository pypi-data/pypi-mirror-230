from eai_commons.utils import time


def test_current_timestamp():
    ct = time.current_timestamp()
    assert len(str(ct)) == 13


def test_to_date_string():
    ct = time.current_timestamp()
    date_str = time.to_date_string(ct, time.DATE_PATTERN)
    print(date_str)
    assert len(date_str) == 10

    date_time_str = time.to_date_string(ct, time.DATE_TIME_PATTERN)
    print(date_time_str)
    assert len(date_time_str) == 19

    iso_time_str = time.to_date_string(ct)
    print(iso_time_str)
    assert len(iso_time_str) == 24


def test_to_unix_timestamp():
    date_str = "2023-09-01 00:00:00"
    ts = time.to_unix_timestamp(date_str, time.DATE_TIME_PATTERN)
    print(ts)
    assert len(str(ts)) == 13
