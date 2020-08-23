from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.window import Window
from .settings import Settings
from .logging import log
from .nvim import call_nvim, get_current_buffer_name, is_buf_visilbe, create_buffer, create_window, win_set_buf
async def local_history_toggle(nvim: Nvim, settings: Settings) -> None:
    def func() -> None:
        buffer = create_buffer(nvim)
        window = create_window(nvim, 30)
        win_set_buf(nvim, window, buffer)

    await call_nvim(nvim, func)
