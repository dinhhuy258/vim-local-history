from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from .settings import Settings
from .logging import log
from .nvim import call_nvim, create_buffer, create_window, win_set_buf, set_current_win, WindowLayout

_LOCAL_HISTORY_FILE_TYPE = 'LocalHistory'

_LOCAL_HISTORY_PREVIEW_FILE_TYPE = 'LocalHistoryPreview'


async def local_history_toggle(settings: Settings) -> None:
    def func() -> None:
        buffer = create_buffer(_LOCAL_HISTORY_FILE_TYPE)
        window = create_window(settings.local_history_width, WindowLayout.LEFT)
        win_set_buf(window, buffer)

        preview_buffer = create_buffer(_LOCAL_HISTORY_PREVIEW_FILE_TYPE)
        preview_window = create_window(settings.local_history_preview_height,
                                       WindowLayout.BELOW)
        win_set_buf(preview_window, preview_buffer)

        set_current_win(window)

    await call_nvim(func)
