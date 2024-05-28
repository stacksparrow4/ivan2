import hashlib

from pathlib import Path

def create_dir_if_not_exists(dir_name):
    Path(dir_name).mkdir(parents=True, exist_ok=True)

def md5(data):
    return hashlib.md5(data.encode()).hexdigest()

def generate_batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]