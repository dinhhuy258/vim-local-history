import os
from pynvim import Nvim
from dataclasses import dataclass
from functools import partial
from typing import Dict
from .nvim import get_global_var, async_call

_DEFAULT_LOCAL_HISTORY_DISABLE = False

_DEFAULT_LOCAL_HISTORY_PATH = '.local_history'

_DEFAULT_LOCAL_HISTORY_SHOW_MESSAGES = True

_DEFAULT_LOCAL_HISTORY_MAX_DISPLAY = 50

_DEFAULT_LOCAL_HISTORY_SAVE_DELAY = 300

_DEFAULT_LOCAL_HISTORY_WIDTH = 45

_DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT = 15

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
    local_history_disable: bool
    local_history_path: str
    local_history_show_messages: bool
    local_history_max_display: int
    local_history_save_delay: int
    local_history_width: int
    local_history_preview_height: int
    local_history_mappings: Dict


async def load_settings() -> Settings:
    local_history_disable = await async_call(
        partial(get_global_var, 'local_history_disable', _DEFAULT_LOCAL_HISTORY_DISABLE))
    local_history_path = await async_call(partial(get_global_var, 'local_history_path', _DEFAULT_LOCAL_HISTORY_PATH))
    if not local_history_path.startswith(os.path.expanduser("~")):
        local_history_path = os.path.join(os.getcwd(), local_history_path)

    local_history_show_messages = await async_call(
        partial(get_global_var, 'local_history_show_messages', _DEFAULT_LOCAL_HISTORY_SHOW_MESSAGES))
    local_history_max_display = await async_call(
        partial(get_global_var, 'local_history_max_display', _DEFAULT_LOCAL_HISTORY_MAX_DISPLAY))
    local_history_save_delay = await async_call(
        partial(get_global_var, 'local_history_save_delay', _DEFAULT_LOCAL_HISTORY_SAVE_DELAY))
    local_history_width = await async_call(partial(get_global_var, 'local_history_width', _DEFAULT_LOCAL_HISTORY_WIDTH))
    local_history_preview_height = await async_call(
        partial(get_global_var, 'local_history_preview_height', _DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT))
    local_history_mappings = await async_call(
        partial(get_global_var, 'local_history_mappings', _DEFAULT_LOCAL_HISTORY_MAPPINGS))
    local_history_mappings = {
        f"LocalHistory_{function}": mappings for function, mappings in local_history_mappings.items()
    }

    return Settings(local_history_disable=local_history_disable,
                    local_history_path=local_history_path,
                    local_history_show_messages=local_history_show_messages,
                    local_history_max_display=max(1, local_history_max_display),
                    local_history_save_delay=max(0, local_history_save_delay),
                    local_history_width=max(1, local_history_width),
                    local_history_preview_height=max(1, local_history_preview_height),
                    local_history_mappings=local_history_mappings)
