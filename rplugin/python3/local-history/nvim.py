import pynvim
from asyncio import Future
from os import linesep
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


async def print_nvim_msg(nvim: pynvim.Nvim,
                         message: Any,
                         error: bool = False,
                         flush: bool = True) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write

    def func() -> None:
        msg = str(message) + (linesep if flush else "")
        write(msg)

    await call_nvim(nvim, func)


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
