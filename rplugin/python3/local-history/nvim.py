from pynvim import Nvim
from pynvim.api.window import Window
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from asyncio import Future
from os import linesep
from typing import Any, Awaitable, Callable, TypeVar, Sequence, Tuple, Iterator

T = TypeVar("T")


def call_nvim(nvim: Nvim, func: Callable[[], T]) -> Awaitable[T]:
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


def get_current_buffer_name(nvim: Nvim) -> str:
    buffer = nvim.api.get_current_buf()
    buffer_name = nvim.api.buf_get_name(buffer)

    return buffer_name


def is_buf_visilbe(nvim: Nvim, buf_name: str) -> bool:
    return int(nvim.api.eval(bufwinnr(bufnr(buf_name)))) != -1


def get_current_win() -> Window:
    return nvim.api.get_current_win()


def create_buffer(nvim: Nvim, file_type: str) -> Buffer:
    options = {"noremap": True, "silent": True, "nowait": True}
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "modifiable", False)
    nvim.api.buf_set_option(buffer, "filetype", file_type)

    return buffer


def find_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = nvim.api.get_current_tabpage()
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not nvim.api.win_get_option(window, "previewwindow"):
            yield window


def create_window(nvim: Nvim, width: int) -> Window:
    split_right = nvim.api.get_option("splitright")

    windows: Sequence[Window] = tuple(window
                                      for window in find_windows_in_tab(nvim))

    focus_win = windows[0]

    nvim.api.set_option("splitright", False)
    nvim.api.set_current_win(focus_win)
    nvim.command(f"{width}vsplit")
    nvim.api.set_option("splitright", split_right)

    window: Window = nvim.api.get_current_win()
    return window


def win_set_buf(nvim: Nvim, window: Window, buffer: Buffer) -> None:
    nvim.api.win_set_buf(window, buffer)


def command(cmd: str) -> None:
    nvim.api.command(cmd)
