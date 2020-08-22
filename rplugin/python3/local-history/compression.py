import bz2


def compress(data):
    return bz2.compress(data.encode('utf-8'))


def decompress(data):
    return bz2.decompress(data).decode('utf-8')
