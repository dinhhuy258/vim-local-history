from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from .settings import Settings
from .logging import log
from .nvim import call_nvim, get_current_buffer_name, create_buffer, create_window, win_set_buf, set_current_win, WindowLayout

_LOCAL_HISTORY_FILE_TYPE = 'LocalHistory'

_LOCAL_HISTORY_PREVIEW_FILE_TYPE = 'LocalHistoryPreview'


async def local_history_toggle(nvim: Nvim, settings: Settings) -> None:
    def func() -> None:
        buffer = create_buffer(nvim, _LOCAL_HISTORY_FILE_TYPE)
        window = create_window(nvim, settings.local_history_width,
                               WindowLayout.LEFT)
        win_set_buf(nvim, window, buffer)

        preview_buffer = create_buffer(nvim, _LOCAL_HISTORY_PREVIEW_FILE_TYPE)
        preview_window = create_window(nvim,
                                       settings.local_history_preview_height,
                                       WindowLayout.BELOW)
        win_set_buf(nvim, preview_window, preview_buffer)

        set_current_win(nvim, window)

    await call_nvim(nvim, func)
