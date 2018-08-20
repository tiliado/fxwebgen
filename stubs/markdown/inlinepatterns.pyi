import typing
from typing import Optional

import markdown as mkd

BRK: str

class Pattern:
    def __init__(self, pattern: str, markdown_instance: Optional[mkd.Markdown] = None) -> None:
        pass

    def handleMatch(self, m: typing.Pattern) -> mkd.util.etree.Element:
        pass


class ImagePattern(Pattern):
    markdown: mkd.Markdown
