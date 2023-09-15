from pathlib import Path
from typing import Callable

from .concatenate import concatenate
from .env import env

Merger = Callable[[bytes, bytes], bytes]


def get(source_name: str, dest_name: str) -> Merger:
    """
    Return the correct file merger
    """

    source_path = Path(source_name)
    dest_path = Path(dest_name)

    source_ext = source_path.suffix or source_path.name
    dest_ext = dest_path.suffix or dest_path.name

    source_type = source_ext.lower()
    dest_type = dest_ext.lower()

    if source_type == ".env" and dest_type == ".env":
        return env
    else:
        return concatenate
