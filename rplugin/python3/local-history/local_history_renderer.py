from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from typing import Optional, Iterator
from .settings import Settings
from .logging import log
from .nvim import (
    async_call,
    create_buffer,
    create_window,
    set_buffer_in_window,
    set_current_window,
    find_windows_in_tab,
    get_buffer_in_window,
    get_buffer_option,
    close_window,
    WindowLayout,
)

_LOCAL_HISTORY_FILE_TYPE = 'LocalHistory'

_LOCAL_HISTORY_PREVIEW_FILE_TYPE = 'LocalHistoryPreview'


def _is_local_history_buffer(buffer: Buffer) -> bool:
    buffer_file_type = get_buffer_option(buffer, 'filetype')
    return buffer_file_type == _LOCAL_HISTORY_FILE_TYPE or buffer_file_type == _LOCAL_HISTORY_PREVIEW_FILE_TYPE


def _find_local_history_windows_in_tab() -> Iterator[Window]:
    for window in find_windows_in_tab():
        buffer: Buffer = get_buffer_in_window(window)
        buffer_file_type = get_buffer_option(buffer, 'filetype')
        if _is_local_history_buffer(buffer):
            yield window


async def local_history_toggle(settings: Settings) -> None:
    def func() -> None:
        windows: Iterator[Window] = _find_local_history_windows_in_tab()
        local_history_opened = False
        for window in windows:
            close_window(window, True)
            local_history_opened = True

        if not local_history_opened:
            buffer = create_buffer(_LOCAL_HISTORY_FILE_TYPE)
            window = create_window(settings.local_history_width,
                                   WindowLayout.LEFT)
            set_buffer_in_window(window, buffer)

            preview_buffer = create_buffer(_LOCAL_HISTORY_PREVIEW_FILE_TYPE)
            preview_window = create_window(
                settings.local_history_preview_height, WindowLayout.BELOW)
            set_buffer_in_window(preview_window, preview_buffer)

            set_current_window(window)

    await async_call(func)
