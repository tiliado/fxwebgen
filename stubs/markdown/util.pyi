# noinspection PyPep8Naming
import xml.etree.ElementTree as etree
from typing import Optional

import markdown as md

STX: str
ETX: str


class Processor:
    markdown: Optional[md.Markdown]

    def __init__(self, markdown_instance: Optional[md.Markdown] = None) -> None:
        pass
