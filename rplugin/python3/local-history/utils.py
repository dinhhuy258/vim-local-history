import bz2
import os
import difflib
from os import path
from asyncio import get_running_loop
from functools import partial
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_in_executor(func: Callable[..., T], *args: Any,
                          **kwargs: Any) -> T:
    loop = get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))


def compress(data: str) -> bytes:
    return bz2.compress(data.encode('utf-8'))


def decompress(data: bytes) -> str:
    return bz2.decompress(data).decode('utf-8')


def get_file_content(file_path: str) -> str:
    file = open(file_path, 'r')
    content = file.read()
    file.close()

    return content


def is_folder_exists(folder_path: str) -> bool:
    return path.exists(folder_path) and path.isdir(folder_path)


def create_folder_if_not_present(folder_path: str) -> None:
    if not is_folder_exists(folder_path):
        os.makedirs(folder_path)


def diff(current: list, history: list) -> list:
    return list(
        difflib.unified_diff(current,
                             history,
                             fromfile='current',
                             tofile='history',
                             lineterm=''))
