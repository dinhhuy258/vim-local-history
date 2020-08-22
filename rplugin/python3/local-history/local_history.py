import pynvim
import base64
from functools import partial
from .nvim import print_nvim_msg
from .asynchronous import run_in_executor
from .file import get_content, create_folder_if_not_present
from .settings import Settings

_LOCAL_HISTORY_FILE_EXTENSION = '.dat'


async def to_local_history_file_name(file_path: str) -> str:
    return base64.b32encode(file_path.encode('utf-8')).decode('utf-8')


async def local_history_save(nvim: pynvim.Nvim, settings: Settings,
                             file_path: str) -> None:
    await run_in_executor(
        partial(create_folder_if_not_present, settings.local_history_path))
    local_history_file_name = await to_local_history_file_name(file_path)
    local_history_file_path = settings.local_history_path + '/' + local_history_file_name + _LOCAL_HISTORY_FILE_EXTENSION
    content = await run_in_executor(partial(get_content, file_path))

    await print_nvim_msg(nvim, 'Get content done: ' + local_history_file_path)
