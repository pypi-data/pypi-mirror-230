from typing import Optional

units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12,
         "K": 10**3, "M": 10**6, "G": 10**9, "T": 10**12,
         "KiB": 2**10, "MiB": 2**20, "GiB": 2**30, "TiB": 2**40,
         "Ki": 2**10, "Mi": 2**20, "Gi": 2**30, "Ti": 2**40,}


def parse_memory(size: str) -> int:
    number: Optional[str] = None
    unit: Optional[str] = None

    for u, n in units.items():
        if size.find(u) != -1:
            unit = u
            number = size[:size.find(u)].strip()

    return int(float(number)*units[unit])
