from typing import List

from markdown import odict
from markdown.util import etree

class BlockParser:
    blockprocessors: odict.OrderedDict

    def parseChunk(self, parent: etree.Element, text: str) -> None:
        pass

    def parseBlocks(self, parent: etree.Element, blocks: List[str]) -> None: ...

