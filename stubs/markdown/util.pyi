# noinspection PyPep8Naming
import xml.etree.ElementTree as etree
from typing import Optional, Any

import markdown as md

STX: str
ETX: str


class Processor:
    markdown: Optional[md.Markdown]

    def __init__(self, markdown_instance: Optional[md.Markdown] = None) -> None:
        pass


class Registry(object):
    def get_index_for_name(self, name: str) -> int: ...
    def register(self, item: Any, name: str, priority: int) -> None: ...
    def deregister(self, name: str, strict: bool = True) -> None: ...
    def add(self, key: str, value: Any, location: str) -> None: ...
