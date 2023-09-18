from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
import time

@contextmanager
def benchmark(description: str = "Unnamed function timer") -> None:
    """Time a function call.

    Run a function with this context manager to time function execution.

    Usage:

    with benchmark("Short description here"):
        ...
    """
    start = time.time()
    yield
    elapsed = time.time() - start

    print(f"{description}: {elapsed} seconds")


@asynccontextmanager
async def async_benchmark(description: str = "Unnamed async function timer") -> None:
    """Time an asynchronous operation.

    Run an async function/operation with this context manager to time function execution.

    Usage:

    with async_benchmark("Short description here"):
        ...
    """
    start = time.monotonic()

    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        print(f"{description}: {elapsed}s")
