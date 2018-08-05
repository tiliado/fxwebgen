import os
from typing import Optional


def file_mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError:
        return -1


def abspath(base_path: Optional[str], path: str) -> str:
    assert path, f'Path must be specified.'
    assert base_path is None or os.path.isabs(base_path), f'Base path "{base_path}" is not absolute.'
    if path.startswith('~'):
        path = os.path.expanduser(path)
    if os.path.isabs(path):
        return path
    return os.path.join(base_path, path) if base_path else os.path.abspath(path)
