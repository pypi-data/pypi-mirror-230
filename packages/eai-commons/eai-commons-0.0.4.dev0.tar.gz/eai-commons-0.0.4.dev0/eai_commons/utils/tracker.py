import typing as t
import functools
from inspect import iscoroutinefunction

from eai_commons.utils.time import current_timestamp, to_date_string, DATE_TIME_PATTERN
from eai_commons.logging import logger


def time_spend(*dargs: t.Any):
    if len(dargs) == 1 and callable(dargs[0]):
        return time_spend()(dargs[0])
    else:

        def decorator(func):
            if iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    begin = current_timestamp()
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        raise e
                    finally:
                        end = current_timestamp()
                        logger.info(
                            f"function=[{func.__module__}.{func.__name__}], spend time: {end - begin}ms, start at: [{to_date_string(begin, DATE_TIME_PATTERN)}]"
                        )

                return async_wrapper
            else:

                def wrapper(*args, **kwargs):
                    begin = current_timestamp()
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        raise e
                    finally:
                        end = current_timestamp()
                        logger.info(
                            f"function=[{func.__module__}.{func.__name__}], spend time: {end - begin}ms, start at: [{to_date_string(begin, DATE_TIME_PATTERN)}]"
                        )

                return wrapper

        return decorator
