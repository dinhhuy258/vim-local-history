import re
from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterator, Tuple, Sequence, Any
from functools import partial
from .graph_log import build_graph_log
from .storage import LocalHistoryStorage, LocalHistoryChange
from .settings import Settings
from .logging import log
from .utils import create_folder_if_not_present, run_in_executor, diff
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
    get_current_cursor,
    set_cursor,
    get_line_count,
    get_line,
    get_lines,
    get_current_line,
    get_width,
    set_width,
    get_height,
    set_height,
    confirm,
    WindowLayout,
)

_LOCAL_HISTORY_FILE_TYPE = 'LocalHistory'

_LOCAL_HISTORY_PREVIEW_FILE_TYPE = 'LocalHistoryPreview'


class MoveDirection(Enum):
    OLDER = 1
    OLDEST = 2
    NEWER = 3
    NEWEST = 4


@dataclass(frozen=True)
class LocalHistoryState:
    current_buffer: Buffer
    changes: OrderedDict


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
    return get_buffer_option(buffer, 'modifiable') and not get_window_option(window, 'previewwindow')


def _close_local_history_windows() -> bool:
    windows: Iterator[Window] = _find_local_history_windows_in_tab()
    closed_local_history_windows = False
    for window in windows:
        close_window(window, True)
        closed_local_history_windows = True

    return closed_local_history_windows


def _buf_set_lines(buffer: Buffer, lines: list, modifiable: bool) -> Iterator[Tuple[str, Sequence[Any]]]:
    if not modifiable:
        yield "nvim_buf_set_option", (buffer, "modifiable", True)

    yield "nvim_buf_set_lines", (buffer, 0, -1, True, [line.rstrip('\n') for line in lines])
    if not modifiable:
        yield "nvim_buf_set_option", (buffer, "modifiable", False)


def _render_local_history_tree(lines: list) -> None:
    _, buffer = find_window_and_buffer_by_file_type(_LOCAL_HISTORY_FILE_TYPE)

    instruction = _buf_set_lines(buffer, lines, False)
    call_atomic(*instruction)


def _render_local_history_preview() -> None:
    if _local_history_state is None:
        return
    target = _get_local_history_target()
    if target is None:
        return

    change: LocalHistoryChange = _local_history_state.changes[target]

    _, buffer = find_window_and_buffer_by_file_type(_LOCAL_HISTORY_PREVIEW_FILE_TYPE)
    preview = diff(
        get_lines(_local_history_state.current_buffer, 0, get_line_count(_local_history_state.current_buffer)),
        change.content)
    instruction = _buf_set_lines(buffer, preview, False)
    call_atomic(*instruction)


def _get_local_history_target() -> Optional[int]:
    window, _ = find_window_and_buffer_by_file_type(_LOCAL_HISTORY_FILE_TYPE)
    set_current_window(window)
    current_line = get_current_line()
    matches = re.match('^[^\[]* \[([0-9]+)\] .*$', current_line)
    if matches:
        return int(matches.group(1))

    return None


async def local_history_delete(settings: Settings) -> None:
    target = await async_call(_get_local_history_target)
    if _local_history_state is None or target is None:
        return

    ans = await async_call(partial(confirm, "Do you want to delete this change?"))
    if ans == False:
        return

    current_file_path = await async_call(partial(get_buffer_name, _local_history_state.current_buffer))
    local_history_storage = LocalHistoryStorage(settings, current_file_path)
    change = _local_history_state.changes[target]
    await run_in_executor(partial(local_history_storage.delete_record, change.change_id))

    index = target
    while _local_history_state.changes.get(index + 1) is not None:
        _local_history_state.changes[index] = _local_history_state.changes[index + 1]
        index = index + 1
    _local_history_state.changes.pop(index)

    window, buffer = await async_call(partial(find_window_and_buffer_by_file_type, _LOCAL_HISTORY_FILE_TYPE))
    row, _ = await async_call(partial(get_current_cursor, window))

    graph = await run_in_executor(partial(build_graph_log, _local_history_state.changes))
    await async_call(partial(_render_local_history_tree, graph))
    line_count = await async_call(partial(get_line_count, buffer))
    await async_call(partial(set_cursor, window, (min(row, line_count), 0)))
    await async_call(_render_local_history_preview)


async def local_history_move(settings: Settings, direction: MoveDirection) -> None:

    def _local_history_move() -> None:
        window = get_current_window()
        buffer = get_buffer_in_window(window)
        row, _ = get_current_cursor(window)
        line_count = get_line_count(buffer)

        if direction == MoveDirection.NEWER:
            new_row = row - 2
        elif direction == MoveDirection.OLDER:
            new_row = row + 2
        elif direction == MoveDirection.NEWEST:
            new_row = 1
        elif direction == MoveDirection.OLDEST:
            new_row = line_count

        if new_row < 1:
            new_row = 1
        elif new_row > line_count:
            new_row = line_count

        new_row_line = get_line(buffer, new_row)
        if new_row_line is None:
            return

        if new_row_line[0] == '|':
            # If we're in between two nodes
            if direction == MoveDirection.NEWER:
                new_row = new_row + 1
            elif direction == MoveDirection.OLDER:
                new_row = new_row - 1

        set_cursor(window, (new_row, 0))

    await async_call(_local_history_move)
    await async_call(_render_local_history_preview)


async def local_history_preview_resize(settings: Settings, direction: int) -> None:

    def _resize() -> None:
        window, _ = find_window_and_buffer_by_file_type(_LOCAL_HISTORY_PREVIEW_FILE_TYPE)
        if window is None:
            return
        height = get_height(window)
        height = height + direction
        set_height(window, height)

    await async_call(_resize)


async def local_history_resize(settings: Settings, direction: int) -> None:

    def _resize() -> None:
        window, _ = find_window_and_buffer_by_file_type(_LOCAL_HISTORY_FILE_TYPE)
        if window is None:
            return
        width = get_width(window)
        width = width + direction
        set_width(window, width)

    await async_call(_resize)


async def local_history_quit(settings: Settings) -> None:
    await async_call(_close_local_history_windows)


async def local_history_revert(settings: Settings) -> None:
    target = await async_call(_get_local_history_target)
    if target is None or _local_history_state is None:
        return
    change = _local_history_state.changes[target]

    def _revert() -> None:
        instruction = _buf_set_lines(_local_history_state.current_buffer, change.content, True)
        call_atomic(*instruction)

    await async_call(_revert)


async def local_history_save(settings: Settings, file_path: str) -> None:
    await run_in_executor(partial(create_folder_if_not_present, settings.local_history_path))

    local_history_storage = LocalHistoryStorage(settings, file_path)
    await run_in_executor(partial(local_history_storage.save_record))
    if settings.local_history_show_messages:
        log.info('[vim-local-history] Save done')


async def local_history_toggle(settings: Settings) -> None:
    global _local_history_state

    _local_history_state = None

    def _toggle() -> Optional[Buffer]:
        windows: Iterator[Window] = _find_local_history_windows_in_tab()
        closed_local_history_windows = _close_local_history_windows()

        if closed_local_history_windows:
            return None
        else:
            current_buffer = get_current_buffer()
            if not _is_buffer_valid(current_buffer):
                log.info('[vim-local-history] Current buffer is not a valid target for vim-local-history')
                return None

            buffer = create_buffer(
                settings.local_history_mappings, {
                    'buftype': 'nofile',
                    'bufhidden': 'hide',
                    'swapfile': False,
                    'buflisted': False,
                    'modifiable': False,
                    'filetype': _LOCAL_HISTORY_FILE_TYPE,
                })
            window = create_window(settings.local_history_width, WindowLayout.LEFT, {
                'list': False,
                'number': False,
                'relativenumber': False,
                'wrap': False,
            })
            set_buffer_in_window(window, buffer)

            preview_buffer = create_buffer(
                dict(), {
                    'buftype': 'nofile',
                    'bufhidden': 'hide',
                    'swapfile': False,
                    'buflisted': False,
                    'modifiable': False,
                    'filetype': _LOCAL_HISTORY_PREVIEW_FILE_TYPE,
                    'syntax': 'diff',
                })
            preview_window = create_window(settings.local_history_preview_height, WindowLayout.BELOW, {
                'number': False,
                'relativenumber': False,
                'wrap': False,
                'foldlevel': 20,
                'foldmethod': 'diff',
            })
            set_buffer_in_window(preview_window, preview_buffer)

            set_current_window(window)

            return current_buffer

    current_buffer = await async_call(_toggle)
    if current_buffer is None:
        return

    current_file_path = await async_call(partial(get_buffer_name, current_buffer))

    local_history_storage = LocalHistoryStorage(settings, current_file_path)
    changes = await run_in_executor(partial(local_history_storage.get_changes))
    local_history_changes = OrderedDict()
    index = 1
    for change in changes:
        local_history_changes[index] = change
        index = index + 1

    graph = await run_in_executor(partial(build_graph_log, local_history_changes))

    # Save the local history state
    _local_history_state = LocalHistoryState(current_buffer, local_history_changes)

    await async_call(partial(_render_local_history_tree, graph))
    await async_call(_render_local_history_preview)
