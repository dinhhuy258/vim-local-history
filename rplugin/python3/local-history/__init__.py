import os
from pynvim import Nvim, plugin, command, autocmd, function
from asyncio import AbstractEventLoop, Lock, run_coroutine_threadsafe
from typing import Any, Awaitable, Callable, Optional, Sequence

from .nvim import init_nvim, get_global_var
from .logging import log, init_log
from .settings import load_settings
from .executor_service import ExecutorService
from .local_history import (
    local_history_save,
    local_history_toggle,
    local_history_quit,
    local_history_move,
    local_history_revert,
    local_history_resize,
    local_history_preview_resize,
    local_history_delete,
    local_history_diff,
    MoveDirection,
)


@plugin
class LocalHistoryPlugin(object):

    def __init__(self, nvim: Nvim) -> None:
        self._nvim = nvim
        self._lock = Lock()
        self._executor = ExecutorService()
        init_nvim(self._nvim)
        init_log(self._nvim)
        self._settings = None
        local_history_workspace = get_global_var('local_history_workspace', os.getcwd())
        os.chdir(local_history_workspace)

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
                if self._settings is None:
                    self._settings = await load_settings()
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

    @function('LocalHistory_revert')
    def revert(self, args: Sequence[Any]) -> None:
        self._run(local_history_revert)

    @function('LocalHistory_delete')
    def delete(self, args: Sequence[Any]) -> None:
        self._run(local_history_delete)

    @function('LocalHistory_move_older')
    def move_older(self, args: Sequence[Any]) -> None:
        self._run(local_history_move, MoveDirection.OLDER)

    @function('LocalHistory_move_oldest')
    def move_oldest(self, args: Sequence[Any]) -> None:
        self._run(local_history_move, MoveDirection.OLDEST)

    @function('LocalHistory_move_newer')
    def move_newer(self, args: Sequence[Any]) -> None:
        self._run(local_history_move, MoveDirection.NEWER)

    @function('LocalHistory_move_newest')
    def move_newest(self, args: Sequence[Any]) -> None:
        self._run(local_history_move, MoveDirection.NEWEST)

    @function('LocalHistory_bigger')
    def bigger(self, args: Sequence[Any]) -> None:
        self._run(local_history_resize, 2)

    @function('LocalHistory_smaller')
    def smaller(self, args: Sequence[Any]) -> None:
        self._run(local_history_resize, -2)

    @function('LocalHistory_preview_bigger')
    def preview_bigger(self, args: Sequence[Any]) -> None:
        self._run(local_history_preview_resize, 2)

    @function('LocalHistory_preview_smaller')
    def preview_smaller(self, args: Sequence[Any]) -> None:
        self._run(local_history_preview_resize, -2)

    @function('LocalHistory_diff')
    def diff(self, args: Sequence[Any]) -> None:
        self._run(local_history_diff)
