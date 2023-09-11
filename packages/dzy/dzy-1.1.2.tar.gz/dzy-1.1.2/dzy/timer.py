import asyncio
import threading
from functools import partial
from typing import Callable, Dict, Iterable, Optional


class RecurringTimer(threading.Thread):
    def __init__(
        self,
        interval: float,
        function: Callable,
        args: Optional[Iterable] = None,
        kwargs: Optional[Dict] = None,
    ):
        args = args or ()
        kwargs = kwargs or {}
        self._function = partial(function, *args, **kwargs)

        self._interval = interval
        self._evloop = asyncio.new_event_loop()

        super().__init__(None, self._evloop.run_forever)

    def start(self):
        super().start()
        self._evloop.call_soon_threadsafe(self._schedule)

    def cancel(self):
        self._evloop.stop()

    def join(self):
        super().join()
        self._evloop.close()

    def _schedule(self):
        self._evloop.call_later(self._interval, self._tick)

    def _tick(self):
        self._function()
        self._schedule()
