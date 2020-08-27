import threading
from pynvim import Nvim, plugin, command, autocmd, function
from asyncio import AbstractEventLoop, Lock, run_coroutine_threadsafe
from typing import Any, Awaitable, Callable, Optional, Sequence

from .nvim import init_nvim
from .logging import log, init_log
from .settings import load_settings
from .executor_service import ExecutorService
from .local_history import (
    local_history_save,
    local_history_toggle,
    local_history_quit,
)


@plugin
class LocalHistoryPlugin(object):
    def __init__(self, nvim: Nvim) -> None:
        self._nvim = nvim
        self._lock = Lock()
        self._executor = ExecutorService()
        init_nvim(self._nvim)
        init_log(self._nvim)
        self._settings = load_settings()

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
                await func(self._settings, *args)

        self._submit(run())

    @autocmd('BufWritePost', pattern='*', eval='expand(\'%:p\')')
    def on_buffer_write_post(self, file_path: str) -> None:
        self._run(local_history_save, file_path)

    @command('LocalHistoryToggle')
    def local_history_toggle_command(self) -> None:
        self._run(local_history_toggle)

    @function('LocalHistory_quit')
    def quit(self, args: Sequence[Any]) -> None:
        self._run(local_history_quit)
