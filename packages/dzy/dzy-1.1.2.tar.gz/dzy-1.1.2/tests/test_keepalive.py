import logging
from unittest.mock import MagicMock, patch

import pytest

from dzy.keepalive import with_keepalives

asap = 0


class TestWithKeepalives:
    @staticmethod
    @pytest.fixture
    def timer_factory():
        with patch("dzy.keepalive.RecurringTimer") as m:
            yield m

    def test_creates_recurring_timer_with_proper_interval(
        self,
        timer_factory: MagicMock,
    ):
        interval = 123

        @with_keepalives(interval=interval)
        def function():
            pass

        function()

        timer_factory.assert_called_once()
        assert ("interval", interval) in (
            timer_factory.call_args_list[0].kwargs.items()
        )

    def test_creates_recurring_timer_that_logs(
        self,
        caplog,
        timer_factory: MagicMock,
    ):
        @with_keepalives()
        def function():
            pass

        function()

        timer_factory.assert_called_once()
        timer_callback = timer_factory.call_args_list[0].kwargs["function"]
        with caplog.at_level(logging.INFO):
            timer_callback("anything")

        assert caplog.messages != []

    @pytest.mark.parametrize("funcname", ["start", "cancel", "join"])
    def test_starts_stops_timer_only_when_function_is_called(
        self,
        timer_factory: MagicMock,
        funcname: str
    ):
        @with_keepalives()
        def function():
            pass

        mockedfunc = getattr(timer_factory(), funcname)
        mockedfunc.assert_not_called()

        function()

        mockedfunc.assert_called_once()

    def test_cancels_timer_when_function_raises(
        self,
        timer_factory: MagicMock,
    ):
        @with_keepalives()
        def function():
            raise Exception("test")

        with pytest.raises(Exception):
            function()

        timer_factory().join.assert_called_once()
        timer_factory().cancel.assert_called_once()

    def test_decorated_function_returns_value(self):
        rv = 123

        @with_keepalives()
        def function():
            return rv

        assert function() == rv

    def test_decorated_function_can_run_many_times(self, times: int = 10):
        mock = MagicMock()
        decorated_func = with_keepalives()(mock)

        for _ in range(times):
            decorated_func()

        assert mock.call_count == times
