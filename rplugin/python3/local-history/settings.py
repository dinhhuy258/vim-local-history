import os
from pynvim import Nvim
from dataclasses import dataclass
from typing import Dict
from .nvim import get_global_var

_DEFAULT_LOCAL_HISTORY_PATH = '.local_history'

_DEFAULT_LOCAL_HISTORY_MAX_DISPLAY = 50

_DEFAULT_LOCAL_HISTORY_SAVE_DELAY = 300

_DEFAULT_LOCAL_HISTORY_WIDTH = 45

_DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT = 15

_DEFAULT_LOCAL_HISTORY_MAPPINGS = {
    'quit': ['q'],
    'move_older': ['j'],
    'move_newer': ['k'],
    'revert': ['<CR>'],
    'bigger': ['+', '='],
    'smaller': ['-', '_'],
}


@dataclass(frozen=True)
class Settings:
    local_history_path: str
    local_history_max_display: int
    local_history_save_delay: int
    local_history_width: int
    local_history_preview_height: int
    local_history_mappings: Dict


def load_settings() -> Settings:
    local_history_path = get_global_var('g:local_history_path') or _DEFAULT_LOCAL_HISTORY_PATH
    if not local_history_path.startswith(os.path.expanduser("~")):
        local_history_path = os.path.join(os.getcwd(), local_history_path)

    local_history_max_display = get_global_var('local_history_max_display') or _DEFAULT_LOCAL_HISTORY_MAX_DISPLAY
    local_history_save_delay = get_global_var('local_history_save_delay') or _DEFAULT_LOCAL_HISTORY_SAVE_DELAY
    local_history_width = get_global_var('local_history_width') or _DEFAULT_LOCAL_HISTORY_WIDTH
    local_history_preview_height = get_global_var(
        'local_history_preview_height') or _DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT
    local_history_mappings = get_global_var('local_history_mappings') or _DEFAULT_LOCAL_HISTORY_MAPPINGS
    local_history_mappings = {
        f"LocalHistory_{function}": mappings for function, mappings in local_history_mappings.items()
    }

    return Settings(local_history_path=local_history_path,
                    local_history_max_display=local_history_max_display,
                    local_history_save_delay=local_history_save_delay,
                    local_history_width=local_history_width,
                    local_history_preview_height=local_history_preview_height,
                    local_history_mappings=local_history_mappings)
