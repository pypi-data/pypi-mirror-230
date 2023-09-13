import os
from pathlib import Path
from typing import Union


def get_size(path: Union[Path, os.DirEntry]):
    total = 0

    if path.is_file():
        return path.stat().st_size

    with os.scandir(path) as it:
        for entry in it:
            total += get_size(entry)

    return total
