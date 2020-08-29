import os
from pynvim import Nvim
from enum import Enum
from dataclasses import dataclass
from functools import partial
from typing import Dict
from .nvim import get_global_var, async_call


class LocalHistoryEnabled(Enum):
    NEVER = 0
    ALWAYS = 1
    WORKSPACE = 2


_DEFAULT_LOCAL_HISTORY_ENABLED = LocalHistoryEnabled.ALWAYS.value

_DEFAULT_LOCAL_HISTORY_PATH = '.local_history'

_DEFAULT_LOCAL_HISTORY_SHOW_INFO_MESSAGES = True

_DEFAULT_LOCAL_HISTORY_MAX_CHANGES = 100

_DEFAULT_LOCAL_HISTORY_NEW_CHANGE_DELAY = 300

_DEFAULT_LOCAL_HISTORY_WIDTH = 45

_DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT = 15

_DEFAULT_LOCAL_HISTORY_EXCLUDE = []

_DEFAULT_LOCAL_HISTORY_MAPPINGS = {
    'quit': ['q'],
    'move_older': ['j', '<down>'],
    'move_newer': ['k', '<up>'],
    'move_oldest': ['G'],
    'move_newest': ['gg'],
    'revert': ['<CR>'],
    'delete': ['d'],
    'bigger': ['L'],
    'smaller': ['H'],
    'preview_bigger': ['K'],
    'preview_smaller': ['J'],
}


@dataclass(frozen=True)
class Settings:
    enabled: LocalHistoryEnabled
    path: str
    show_info_messages: bool
    max_changes: int
    new_change_delay: int
    width: int
    preview_height: int
    exclude: list
    mappings: Dict


async def load_settings() -> Settings:
    enabled_value = await async_call(partial(get_global_var, 'local_history_enabled', _DEFAULT_LOCAL_HISTORY_ENABLED))
    enabled = LocalHistoryEnabled.ALWAYS
    if enabled_value == LocalHistoryEnabled.NEVER.value:
        enabled = LocalHistoryEnabled.NEVER
    elif enabled_value == LocalHistoryEnabled.WORKSPACE.value:
        enabled = LocalHistoryEnabled.WORKSPACE

    path = await async_call(partial(get_global_var, 'local_history_path', _DEFAULT_LOCAL_HISTORY_PATH))
    if not path.startswith(os.path.expanduser("~")):
        path = os.path.join(os.getcwd(), path)

    show_info_messages = await async_call(
        partial(get_global_var, 'local_history_show_info_messages', _DEFAULT_LOCAL_HISTORY_SHOW_INFO_MESSAGES))
    max_changes = await async_call(
        partial(get_global_var, 'local_history_max_changes', _DEFAULT_LOCAL_HISTORY_MAX_CHANGES))
    new_change_delay = await async_call(
        partial(get_global_var, 'local_history_new_change_delay', _DEFAULT_LOCAL_HISTORY_NEW_CHANGE_DELAY))
    width = await async_call(partial(get_global_var, 'local_history_width', _DEFAULT_LOCAL_HISTORY_WIDTH))
    preview_height = await async_call(
        partial(get_global_var, 'local_history_preview_height', _DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT))
    exclude = await async_call(partial(get_global_var, 'local_history_exclude', _DEFAULT_LOCAL_HISTORY_EXCLUDE))
    mappings = await async_call(partial(get_global_var, 'local_history_mappings', _DEFAULT_LOCAL_HISTORY_MAPPINGS))
    mappings = {f"LocalHistory_{function}": mappings for function, mappings in mappings.items()}

    return Settings(enabled=enabled,
                    path=path,
                    show_info_messages=show_info_messages,
                    max_changes=max(1, max_changes),
                    new_change_delay=max(0, new_change_delay),
                    width=max(1, width),
                    preview_height=max(1, preview_height),
                    exclude=exclude,
                    mappings=mappings)
