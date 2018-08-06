# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Optional, cast, Dict

from fxwebgen.context import Context
from fxwebgen.objects import Thumbnail
from fxwebgen.typing import StrDict


# pylint: disable=too-many-instance-attributes
class Page:
    source: str
    target: Optional[str]
    default_path: str
    body: Optional[str]
    toc: Optional[str]
    metadata: StrDict
    references: dict
    thumbnails: Dict[str, Thumbnail]
    ctx: Context

    @classmethod
    def test(cls, path: str) -> bool:
        raise NotImplementedError

    def __init__(self, ctx: Context, source: str, default_path: str) -> None:
        self.ctx = ctx
        self.default_path = default_path
        self.source = source
        self.body = None
        self.metadata = {}
        self.references = {}
        self.thumbnails = {}
        self.toc = None
        self.target = None

    def process(self) -> None:
        raise NotImplementedError

    @property
    def webroot(self) -> str:
        return cast(str, self.metadata['webroot'])

    @property
    def path(self) -> str:
        return self.metadata.get('path') or self.default_path

    @property
    def filename(self) -> str:
        return cast(str, self.metadata['filename'])
