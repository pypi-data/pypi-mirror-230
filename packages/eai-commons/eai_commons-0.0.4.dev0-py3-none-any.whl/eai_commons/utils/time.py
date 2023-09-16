import pytz
import time
from datetime import datetime

from typing import Optional

ISO_TIME_PATTERN = "%Y-%m-%dT%H:%M:%S%z"
DATE_TIME_PATTERN = "%Y-%m-%d %H:%M:%S"
DATE_PATTERN = "%Y-%m-%d"
_LOCAL_TIMEZONE = pytz.timezone("Asia/Shanghai")


def current_timestamp():
    """
    获取13位时间戳
    """
    return int(time.time() * 1000)


def to_date_string(
    unix_timestamp: Optional[int] = None, pattern: str = ISO_TIME_PATTERN
) -> Optional[str]:
    """
    将 unix 时间戳转换为指定格式的时间字符串
    :param unix_timestamp: unix时间戳
    :param pattern: 返回格式，默认为iso格式
    :return:
    """
    if unix_timestamp is None:
        return None

    dt = datetime.fromtimestamp(unix_timestamp / 1000, tz=_LOCAL_TIMEZONE)
    return dt.strftime(pattern)


def to_unix_timestamp(date_string: str, pattern: str = ISO_TIME_PATTERN):
    return int(datetime.strptime(date_string, pattern).timestamp() * 1000)
