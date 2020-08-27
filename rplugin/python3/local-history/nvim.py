from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim.api.window import Window
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from enum import Enum
from asyncio import Future
from os import linesep
from typing import (
    Any,
    Awaitable,
    Callable,
    TypeVar,
    Sequence,
    Tuple,
    Iterator,
    Optional,
    Dict,
)

T = TypeVar("T")


class WindowLayout(Enum):
    LEFT = 1
    BELOW = 2


def init_nvim(nvim: Nvim) -> None:
    global _nvim
    _nvim = nvim


def call_atomic(*instructions: Tuple[str, Sequence[Any]]) -> None:
    inst = tuple(
        (f"{instruction}", args) for instruction, args in instructions)
    out, error = _nvim.api.call_atomic(inst)
    if error:
        raise NvimError(error)


def async_call(func: Callable[[], T]) -> Awaitable[T]:
    future: Future = Future()

    def run() -> None:
        try:
            ret = func()
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(ret)

    _nvim.async_call(run)
    return future


def get_current_window() -> None:
    return _nvim.api.get_current_win()


def create_buffer(file_type: str, keymaps: Dict[str, str] = dict()) -> Buffer:
    options = {"noremap": True, "silent": True, "nowait": True}
    buffer: Buffer = _nvim.api.create_buf(False, True)
    _nvim.api.buf_set_option(buffer, "modifiable", False)
    _nvim.api.buf_set_option(buffer, "filetype", file_type)
    for mapping, function in keymaps.items():
        _nvim.api.buf_set_keymap(buffer, "n", mapping,
                                 f"<cmd>call {function}(v:false)<cr>", options)

    return buffer


def find_windows_in_tab() -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = _nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = _nvim.api.get_current_tabpage()
    windows: Sequence[Window] = _nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not _nvim.api.win_get_option(window, "previewwindow"):
            yield window


def create_window(size: int, layout: WindowLayout) -> Window:
    split_right = _nvim.api.get_option("splitright")
    split_below = _nvim.api.get_option("splitbelow")

    windows: Sequence[Window] = tuple(window
                                      for window in find_windows_in_tab())

    focus_win = windows[0]

    _nvim.api.set_current_win(focus_win)
    if layout is WindowLayout.LEFT:
        _nvim.api.set_option("splitright", False)
        _nvim.command(f"{size}vsplit")
    else:
        _nvim.api.set_option("splitbelow", True)
        _nvim.command(f"{size}split")

    _nvim.api.set_option("splitright", split_right)
    _nvim.api.set_option("splitbelow", split_below)

    window: Window = _nvim.api.get_current_win()
    return window


def close_window(window: Window, force: bool) -> None:
    _nvim.api.win_close(window, force)


def get_window_option(window: Window, option: str) -> str:
    return _nvim.api.win_get_option(window, option)


def get_buffer_option(buffer: Buffer, option: str) -> str:
    return _nvim.api.buf_get_option(buffer, option)


def set_buffer_in_window(window: Window, buffer: Buffer) -> None:
    _nvim.api.win_set_buf(window, buffer)


def get_buffer_in_window(window: Window) -> Buffer:
    return _nvim.api.win_get_buf(window)


def find_window_and_buffer_by_file_type(
        file_type: str) -> Optional[Tuple[Window, Buffer]]:
    for window in _nvim.api.list_wins():
        buffer: Buffer = _nvim.api.win_get_buf(window)
        if file_type == _nvim.api.buf_get_option(buffer, "filetype"):
            return window, buffer

    return None


def get_current_buffer() -> Buffer:
    return _nvim.api.get_current_buf()


def get_buffer_name(buffer: Buffer) -> str:
    return _nvim.api.buf_get_name(buffer)


def command(cmd: str) -> None:
    _nvim.api.command(cmd)


def set_current_window(window: Window) -> None:
    _nvim.api.set_current_win(window)


def get_global_var(name: str) -> Optional[Any]:
    try:
        return _nvim.api.get_var(name)
    except:
        return None
