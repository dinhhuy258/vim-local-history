import pynvim
from functools import partial
from .nvim import print_nvim_msg
from .asynchronous import run_in_executor
from .file import get_content


async def local_history_save(nvim: pynvim.Nvim, path: str) -> None:
    content = await run_in_executor(partial(get_content, path))
    await print_nvim_msg(nvim, 'Get content done')
