import time

from eai_commons.utils.tracker import time_spend
from eai_commons.utils.sync import run_until_complete


class TestTimeSpend:
    @classmethod
    @time_spend
    def class_run(cls, t):
        time.sleep(t)

    @staticmethod
    @time_spend
    def static_run(t):
        time.sleep(t)

    @time_spend
    def self_run(self, t):
        time.sleep(t)

    @time_spend
    async def self_async_run(self, t):
        time.sleep(t)


def test_time_spend():
    @time_spend
    def _do_some_jobs():
        time.sleep(0.2)

    _do_some_jobs()

    @time_spend
    async def _do_some_async_jobs():
        time.sleep(0.2)

    run_until_complete(_do_some_async_jobs())

    TestTimeSpend.class_run(0.2)
    TestTimeSpend.static_run(0.2)
    TestTimeSpend().self_run(0.2)
    run_until_complete(TestTimeSpend().self_async_run(0.2))
