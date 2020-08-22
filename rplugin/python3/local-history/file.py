import pynvim
import os
from os import path
from .asynchronous import run_in_executor
from .nvim import print_nvim_msg


def get_content(file_path: str) -> str:
    file = open(file_path, 'r')
    content = file.read()
    file.close()

    return content


def is_folder_exists(folder_path: str) -> bool:
    return path.exists(folder_path) and path.isdir(folder_path)


def create_folder_if_not_present(folder_path: str) -> None:
    if not is_folder_exists(folder_path):
        os.mkdir(folder_path)
