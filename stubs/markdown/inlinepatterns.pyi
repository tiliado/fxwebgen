import typing
from typing import Optional

import markdown as mkd

IMAGE_LINK_RE: str

class Pattern:
    def __init__(self, pattern: str, markdown_instance: Optional[mkd.Markdown] = None) -> None:
        pass

    def handleMatch(self, m: typing.Pattern, data: typing.Any) \
            -> typing.Tuple[Optional[mkd.util.etree.Element], Optional[int], Optional[int]]:
        pass

class InlineProcessor(Pattern):
    ...

class ImageInlineProcessor(InlineProcessor):
    markdown: mkd.Markdown
