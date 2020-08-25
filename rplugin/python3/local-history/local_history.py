from functools import partial
from typing import Iterator
from .local_history_storage import LocalHistoryStorage, LocalHistoryChange
from .asynchronous import run_in_executor
from .file import create_folder_if_not_present, is_file_exists
from .settings import Settings
from .logging import log


async def get_local_history_changes(
        settings: Settings, file_path: str) -> Iterator[LocalHistoryChange]:
    if not is_file_exists(file_path):
        return iter(())

    local_history_storage = LocalHistoryStorage(settings, file_path)
    return await run_in_executor(partial(local_history_storage.get_changes))


async def local_history_save(settings: Settings, file_path: str) -> None:
    await run_in_executor(
        partial(create_folder_if_not_present, settings.local_history_path))

    local_history_storage = LocalHistoryStorage(settings, file_path)
    await run_in_executor(partial(local_history_storage.save_record))
    log.info('Save patch done!!!')
