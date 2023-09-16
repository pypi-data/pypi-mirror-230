import time

from inspect import iscoroutinefunction
from threading import BoundedSemaphore
from collections.abc import Collection
from typing import Callable, Any

from tqdm import tqdm

from eai_commons.utils.time import current_timestamp, to_date_string, DATE_TIME_PATTERN
from eai_commons.logging import logger


def _section_run(
    function_call, iterator, batch_size: int, time_window_sec: int = 0
) -> Collection | None:
    if not isinstance(iterator, Collection):
        return function_call(iterator)

    total_rows = len(iterator)
    if total_rows <= batch_size:
        return function_call(iterator)

    results = []
    func_result_type = None

    for offset in tqdm(
        range(0, total_rows, batch_size), total=total_rows // batch_size + 1
    ):
        batch_id = offset // batch_size
        sub_iterator = iterator[offset : offset + batch_size]
        logger.info(
            f"batch id: {batch_id}, batch size: {len(sub_iterator)}, total tasks: {total_rows}, processing..."
        )
        begin = current_timestamp()

        sub_results = function_call(sub_iterator)
        if sub_results:
            func_result_type = func_result_type or type(sub_results)
            results.extend(sub_results)

        logger.info(
            f"batch id: {batch_id}, sub tasks size: {len(sub_iterator)}, total tasks: {total_rows}, done."
        )

        # 最后一批，不用休眠
        if len(sub_iterator) < batch_size:
            continue
        # 限速
        elapsed = current_timestamp() - begin
        sleep = time_window_sec * 1000 - elapsed
        if sleep > 0:
            logger.info(f"request limit, sleep {sleep}ms before next batch.")
            time.sleep(sleep / 1000)

    if func_result_type:
        return func_result_type(results)
    return None


def section_run(batch_size: int, time_window_sec: int = 0):
    def decorator(func):
        if iscoroutinefunction(func):
            raise ValueError(
                "section_run support blocking function. don't use in async function!"
            )

        def wrapper(obj0=None, obj1=None, /, *args, **kwargs):
            if not obj0:
                return func(*args, **kwargs)
            iterator, class_inner_method = obj0, False
            if not isinstance(iterator, Collection):
                if obj1:
                    iterator, class_inner_method = obj1, True
                else:
                    return func(obj0, *args, **kwargs)
            if not isinstance(iterator, Collection):
                return func(obj0, obj1, *args, **kwargs)

            if class_inner_method:
                function_call: Callable[[Any], Any] = lambda sub_iter: func(obj0, sub_iter, *args, **kwargs)
            else:
                function_call: Callable[[Any], Any] = lambda sub_iter: func(sub_iter, *args, **kwargs)

            begin = current_timestamp()
            logger.info(f"section_run start. batch_size = {batch_size}")
            results = _section_run(function_call, iterator, batch_size, time_window_sec)
            end = current_timestamp()
            logger.info(
                f"section_run end. time spend: {end - begin}ms, start at: [{to_date_string(begin, DATE_TIME_PATTERN)}]"
            )
            return results

        return wrapper

    return decorator


class RateControl:
    def __init__(self, rate_max: int, timeout_sec: int) -> None:
        self.rate_max = rate_max
        self.timeout_sec = timeout_sec
        self.semaphore = BoundedSemaphore(rate_max)

    def control(self, func, *args, **kwargs):
        lock_ = self.semaphore.acquire(timeout=self.timeout_sec)
        if lock_:
            try:
                return func(*args, **kwargs)
            finally:
                self.semaphore.release()

    async def async_control(self, func, *args, **kwargs):
        lock_ = self.semaphore.acquire(timeout=self.timeout_sec)
        if lock_:
            try:
                return await func(*args, **kwargs)
            finally:
                self.semaphore.release()
