import os
from pynvim import Nvim
from dataclasses import dataclass
from .nvim import get_global_var

_DEFAULT_LOCAL_HISTORY_PATH = '.local_history'

_DEFAULT_LOCAL_HISTORY_MAX_DISPLAY = 50

_DEFAULT_LOCAL_HISTORY_SAVE_DELAY = 300

_DEFAULT_LOCAL_HISTORY_WIDTH = 45

_DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT = 15


@dataclass(frozen=True)
class Settings:
    local_history_path: str
    local_history_max_display: int
    local_history_save_delay: int
    local_history_width: int
    local_history_preview_height: int


def load_settings(nvim: Nvim) -> Settings:
    local_history_path = get_global_var(
        nvim, 'g:local_history_path') or _DEFAULT_LOCAL_HISTORY_PATH
    if not local_history_path.startswith(os.path.expanduser("~")):
        local_history_path = os.path.join(os.getcwd(), local_history_path)

    local_history_max_display = get_global_var(
        nvim,
        'g:local_history_max_display') or _DEFAULT_LOCAL_HISTORY_MAX_DISPLAY
    local_history_save_delay = get_global_var(
        nvim,
        'g:local_history_save_delay') or _DEFAULT_LOCAL_HISTORY_SAVE_DELAY
    local_history_width = get_global_var(
        nvim, 'g:local_history_width') or _DEFAULT_LOCAL_HISTORY_WIDTH
    local_history_preview_height = get_global_var(
        nvim, 'g:local_history_preview_height'
    ) or _DEFAULT_LOCAL_HISTORY_PREVIEW_HEIGHT

    return Settings(local_history_path=local_history_path,
                    local_history_max_display=local_history_max_display,
                    local_history_save_delay=local_history_save_delay,
                    local_history_width=local_history_width,
                    local_history_preview_height=local_history_preview_height)
