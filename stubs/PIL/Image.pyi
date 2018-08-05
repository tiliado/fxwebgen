import pathlib
from typing import Union, IO, Optional, Any


class Image:
    format: Optional[str]
    def save(self, fp: Union[str, pathlib.Path, IO[bytes]], format: Optional[str] = None, **params: Any) -> None: ...

def open(fp: Union[str, pathlib.Path, IO[bytes]], mode: str = "r") -> Image: ...

