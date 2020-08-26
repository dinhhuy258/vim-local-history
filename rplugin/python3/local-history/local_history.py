from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from collections import OrderedDict
from typing import Optional, Iterator, Tuple, Sequence, Any
from functools import partial
from .graph_log import build_graph_log
from .storage import LocalHistoryStorage, LocalHistoryChange
from .settings import Settings
from .logging import log
from .utils import create_folder_if_not_present, run_in_executor
from .nvim import (
    async_call,
    call_atomic,
    create_buffer,
    create_window,
    close_window,
    set_buffer_in_window,
    set_current_window,
    find_windows_in_tab,
    get_buffer_in_window,
    get_buffer_option,
    get_window_option,
    get_current_buffer,
    get_current_window,
    get_buffer_name,
    find_window_and_buffer_by_file_type,
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


def _is_buffer_valid(buffer: Buffer) -> str:
    file_type = get_buffer_option(buffer, 'filetype')
    if file_type == 'help' or file_type == 'quickfix' or file_type == 'terminal':
        return False

    window = get_current_window()
    return get_buffer_option(buffer, 'modifiable') and not get_window_option(
        window, 'previewwindow')


async def local_history_save(settings: Settings, file_path: str) -> None:
    await run_in_executor(
        partial(create_folder_if_not_present, settings.local_history_path))

    local_history_storage = LocalHistoryStorage(settings, file_path)
    await run_in_executor(partial(local_history_storage.save_record))
    log.info('Save patch done!!!')


async def local_history_toggle(settings: Settings) -> None:
    global local_history_changes

    def _toggle() -> Optional[str]:
        windows: Iterator[Window] = _find_local_history_windows_in_tab()
        local_history_opened = False
        for window in windows:
            close_window(window, True)
            local_history_opened = True

        if local_history_opened:
            return
        else:
            buffer = get_current_buffer()
            if not _is_buffer_valid(buffer):
                log.info(
                    '[vim-local-history] Current buffer is not a valid target for vim-local-history'
                )
                return None

            current_file_path = get_buffer_name(buffer)

            buffer = create_buffer(_LOCAL_HISTORY_FILE_TYPE)
            window = create_window(settings.local_history_width,
                                   WindowLayout.LEFT)
            set_buffer_in_window(window, buffer)

            preview_buffer = create_buffer(_LOCAL_HISTORY_PREVIEW_FILE_TYPE)
            preview_window = create_window(
                settings.local_history_preview_height, WindowLayout.BELOW)
            set_buffer_in_window(preview_window, preview_buffer)

            set_current_window(window)

            return current_file_path

    file_path = await async_call(_toggle)

    if not file_path:
        return

    local_history_storage = LocalHistoryStorage(settings, file_path)
    changes = await run_in_executor(partial(local_history_storage.get_changes))
    local_history_changes = OrderedDict()
    index = 1
    for change in changes:
        local_history_changes[index] = change
        ++index

    graph = await run_in_executor(
        partial(build_graph_log, local_history_changes))

    def _render_local_history_tree():
        window, buffer = find_window_and_buffer_by_file_type(
            _LOCAL_HISTORY_FILE_TYPE)

        def _buf_set_lines(buffer: Buffer,
                           lines: list) -> Iterator[Tuple[str, Sequence[Any]]]:
            yield "nvim_buf_set_option", (buffer, "modifiable", True)
            yield "nvim_buf_set_lines", (buffer, 0, -1, True, graph)
            yield "nvim_buf_set_option", (buffer, "modifiable", False)

        instruction = _buf_set_lines(buffer, graph)
        call_atomic(*instruction)

    await async_call(_render_local_history_tree)
