import bz2


def compress(data: str) -> bytes:
    return bz2.compress(data.encode('utf-8'))


def decompress(data: bytes) -> str:
    return bz2.decompress(data).decode('utf-8')
