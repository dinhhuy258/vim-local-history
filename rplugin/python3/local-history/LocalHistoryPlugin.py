import pynvim
import threading
from asyncio import AbstractEventLoop, Lock, run_coroutine_threadsafe
from typing import Any, Awaitable, Callable, Optional, Sequence

from .logging import log, init_log
from .nvim import print_nvim_msg
from .local_history import local_history_save
from .ExecutorService import ExecutorService


@pynvim.plugin
class LocalHistoryPlugin(object):
    def __init__(self, nvim: pynvim.Nvim):
        self._nvim = nvim
        self._lock = Lock()
        self._executor = ExecutorService()
        init_log(self._nvim)

    def _submit(self, coro: Awaitable[None]) -> None:
        loop: AbstractEventLoop = self._nvim.loop

        def submit() -> None:
            future = run_coroutine_threadsafe(coro, loop)

            try:
                future.result()
            except Exception as e:
                log.exception("%s", str(e))

        self._executor.run_sync(submit)

    def _run(self, func: Callable[..., Awaitable[None]], *args: Any) -> None:
        async def run() -> None:
            async with self._lock:
                await func(self._nvim, *args)

        self._submit(run())

    @pynvim.autocmd('BufWritePost', pattern='*', eval='expand(\'%:p\')')
    def on_buffer_write_post(self, path: str):
        self._run(local_history_save, path)
