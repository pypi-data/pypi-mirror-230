import asyncio

from eai_commons.utils import sync


def test_run_until_complete():
    coroutine = _do_some_jobs()
    sync.run_until_complete(coroutine)


async def _do_some_jobs():
    print("async do something")
    await asyncio.sleep(1)

