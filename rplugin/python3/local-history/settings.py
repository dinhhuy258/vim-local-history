import pynvim
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    local_history_path: str
    local_history_max_display: int
    local_history_save_delay: int


def load_settings(nvim: pynvim.Nvim) -> Settings:
    local_history_path = nvim.eval('g:local_history_path')
    local_history_max_display = nvim.eval('g:local_history_max_display')
    local_history_save_delay = nvim.eval('g:local_history_save_delay')

    return Settings(local_history_path=local_history_path,
                    local_history_max_display=local_history_max_display,
                    local_history_save_delay=local_history_save_delay)
