# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Optional


class Thumbnail:
    original_url: str
    width: Optional[int]
    height: Optional[int]
    filename: str

    def __init__(self, original_url: str,
                 width: Optional[int],
                 height: Optional[int]) -> None:
        assert width or height, f'No width or height specified for "{original_url}."'
        self.original_url = original_url
        self.width = width
        self.height = height
        basename, extension = original_url.rsplit('.', 1)
        self.filename = f'{basename}[{width or ""}x{height or ""}].{extension}'

    def __str__(self) -> str:
        return f'Thumbnail[{self.filename}]'

    __repr__ = __str__
