import pynvim
from asyncio import Future
from os import linesep
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


def call_nvim(nvim: pynvim.Nvim, func: Callable[[], T]) -> Awaitable[T]:
    future: Future = Future()

    def run() -> None:
        try:
            ret = func()
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(ret)

    nvim.async_call(run)
    return future
