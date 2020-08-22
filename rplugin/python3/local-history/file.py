import pynvim
from .asynchronous import run_in_executor
from .nvim import print_nvim_msg


def get_content(path: str) -> str:
    file = open(path, 'r')
    content = file.read()
    file.close()

    return content
