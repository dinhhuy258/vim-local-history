import shelve
import time
from os import path
from dataclasses import dataclass
from hashlib import md5
from .settings import Settings
from .file import get_file_content
from .compression import compress

_LOCAL_HISTORY_HEADER = 'header'

_LOCAL_HISTORY_FIRST_RECORD_ID = 1

_LOCAL_HISTORY_NO_RECORD = 0


@dataclass(frozen=False)
class LocalHistoryChangePatch:
    record_id: int
    timestamp: float
    content: bytes
    next_record_id: int


@dataclass(frozen=False)
class LocalHistoryHeader:
    num_records: int
    first_record_id: int
    last_record_id: int


class LocalHistoryStorage:
    def __init__(self, settings: Settings, file_path: str) -> None:
        self._settings = settings
        self._file_path = file_path
        self._local_history_file_path = path.join(
            settings.local_history_path,
            self._get_local_history_file_name(file_path))

    def save_patch(self) -> None:
        content = get_file_content(self._file_path)
        if not content:
            # Don't backup empty file
            return
        current_timestamp = time.time()
        with shelve.open(self._local_history_file_path) as local_history_file:
            header = local_history_file.get(_LOCAL_HISTORY_HEADER)
            if header is None:
                header = LocalHistoryHeader(_LOCAL_HISTORY_NO_RECORD,
                                            _LOCAL_HISTORY_NO_RECORD,
                                            _LOCAL_HISTORY_NO_RECORD)

            # Reduce the content size
            compressionContent = compress(content)

            if header.last_record_id == _LOCAL_HISTORY_NO_RECORD:
                # Store patch and header
                local_history_change_patch = LocalHistoryChangePatch(
                    _LOCAL_HISTORY_FIRST_RECORD_ID, current_timestamp,
                    compressionContent, _LOCAL_HISTORY_NO_RECORD)
                local_history_file[str(local_history_change_patch.record_id
                                       )] = local_history_change_patch

                header.num_records = 1
                header.first_record_id = local_history_change_patch.record_id
                header.last_record_id = local_history_change_patch.record_id
                local_history_file[_LOCAL_HISTORY_HEADER] = header

                return

            last_record = local_history_file[str(header.last_record_id)]
            if current_timestamp - last_record.timestamp < self._settings.local_history_save_delay:
                # Update the content of the last record in the case duration between current timestamp and timestamp of the last record is less than save delay
                last_record.content = compressionContent
                # FIXME: Should we update the timestamp value?
                local_history_file[str(header.last_record_id)] = last_record
                return

            # Store patch
            local_history_change_patch = LocalHistoryChangePatch(
                header.last_record_id + 1, current_timestamp,
                compressionContent, _LOCAL_HISTORY_NO_RECORD)
            local_history_file[str(local_history_change_patch.record_id
                                   )] = local_history_change_patch

            # Update the last record
            last_record.next_record_id = local_history_change_patch.record_id
            local_history_file[str(last_record.record_id)] = last_record

            # Update header
            header.num_records += 1
            header.last_record_id = local_history_change_patch.record_id

            if header.num_records > self._settings.local_history_max_display:
                # Remove the first_record
                first_record = local_history_file[str(header.first_record_id)]
                new_first_record_id = first_record.record_id
                del local_history_file[str(header.first_record_id)]
                # Update new first record into the header
                header.first_record_id = new_first_record_id

            # Update header
            local_history_file[_LOCAL_HISTORY_HEADER] = header

    def _get_local_history_file_name(self, file_path: str) -> str:
        return md5(file_path.encode('utf-8')).hexdigest()