from typing import Callable
from unittest.mock import MagicMock

from dzy.timer import RecurringTimer

asap = 0
never = 24 * 3600  # tomorrow (24h) in seconds


def callchain(*chain) -> Callable:
    chain = iter(chain)

    def wrapper():
        fn = next(chain)
        fn = (lambda: None) if isinstance(fn, type(...)) else fn
        return fn()

    return wrapper


class TestRecurringTimer:
    def setup_method(self):
        self.function = MagicMock()

    def test_timer_can_be_canceled_before_first_execution(self):
        timer = RecurringTimer(never, self.function)
        timer.start()

        timer.cancel()
        timer.join()

        self.function.assert_not_called()

    def test_timer_stops_after_few_executions(self):
        timer = RecurringTimer(asap, self.function)
        self.function.side_effect = callchain(..., ..., timer.cancel)

        timer.start()
        timer.join()

        assert self.function.call_count == 3

    def test_timer_passes_arguments(self):
        args = ("1", 2, 3.14)
        kwargs = {"foo": "bar"}
        timer = RecurringTimer(asap, self.function, args, kwargs)
        self.function.side_effect = lambda *a, **kw: timer.cancel()

        timer.start()
        timer.join()

        self.function.assert_called_once_with(*args, **kwargs)
