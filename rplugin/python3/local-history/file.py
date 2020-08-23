import pynvim
import os
from os import path


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
