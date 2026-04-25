from __future__ import annotations
from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar, cast


F = TypeVar("F", bound = Callable[..., Any])


def timed(function: F) -> F:
    """decorator that keeps the original return value and stores the elapsed time.

    The wrapped function behaves exactly the same as the original one. The only
    extra behaviour is that the wrapper exposes the attribute
    ``last_elapsed_seconds`` after each call.
    """

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        result = function(*args, **kwargs)
        wrapper.last_elapsed_seconds = perf_counter() - start
        return result

    wrapper.last_elapsed_seconds = 0.0
    return cast(F, wrapper)
