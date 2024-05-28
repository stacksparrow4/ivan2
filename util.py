import hashlib
import re
import os

from pathlib import Path

def create_dir_if_not_exists(dir_name):
    Path(dir_name).mkdir(parents=True, exist_ok=True)

def md5(data):
    return hashlib.md5(data.encode()).hexdigest()

def extract_dot_points(data):
    new_lines = []
    for l in data.splitlines():
        if re.match(r"^(\*|[0-9]+\.) ", l):
            new_lines.append(re.sub(r"^[0-9]+\. ", "* ", l))
    return "\n".join(new_lines)

def write_to_path(fpath, data):
    create_dir_if_not_exists(os.path.dirname(fpath))

    with open(fpath, "w") as f:
        f.write(data)

def get_llama_hosts():
    return [h.strip() for h in os.environ.get("LLAMA_HOSTS").split(",")]

def generate_batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def generate_n_batches(iterable, n):
    return generate_batches(iterable, len(iterable) // n + 1)