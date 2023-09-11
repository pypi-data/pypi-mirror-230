from collections.abc import Callable
import time
from typing import Any, TypeVar

import wrapt

T = TypeVar("T")


@wrapt.decorator
def timer(func: Callable[..., T], instance: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> T:
    """Calculates the execution time for the decorated method."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()

    print(f"Time executing '{func.__name__}' = {end - start} s")

    return result
