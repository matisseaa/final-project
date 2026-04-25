import pytest
import time

from src.decorators import timed

# timed decorator tests

def test_timed_basic():
    @timed
    def f():
        return 42

    result = f()

    assert result == 42
    assert hasattr(f, "last_elapsed_seconds")
    assert f.last_elapsed_seconds >= 0


def test_timed_measures_time():
    @timed
    def slow_function():
        time.sleep(0.01)
        return "done"

    slow_function()

    assert slow_function.last_elapsed_seconds > 0


def test_timed_preserves_return_value():
    @timed
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


def test_timed_multiple_calls_updates_time():
    @timed
    def f():
        return 1

    f()
    first_time = f.last_elapsed_seconds

    f()
    second_time = f.last_elapsed_seconds

    assert second_time >= 0