import pynvim
from functools import partial
from .local_history_storage import LocalHistoryStorage
from .asynchronous import run_in_executor
from .file import create_folder_if_not_present
from .settings import Settings
from .logging import log


async def local_history_save(nvim: pynvim.Nvim, settings: Settings,
                             file_path: str) -> None:
    await run_in_executor(
        partial(create_folder_if_not_present, settings.local_history_path))

    local_history_storage = LocalHistoryStorage(settings, file_path)
    await run_in_executor(partial(local_history_storage.save_patch))
    log.info('Save patch done!!!')
