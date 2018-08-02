# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Optional

from fxwebgen.typing import StrDict


class Page:
    path: str
    body: Optional[str]
    metadata: StrDict
    references: dict

    def __init__(self, path: str) -> None:
        self.path = path
        self.body = None
        self.metadata = {}
        self.references = {}

    def process(self) -> None:
        raise NotImplementedError
