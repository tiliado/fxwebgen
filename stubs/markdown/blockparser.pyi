from typing import List

from markdown.util import etree, Registry

class BlockParser:
    blockprocessors: Registry

    def parseChunk(self, parent: etree.Element, text: str) -> None:
        pass

    def parseBlocks(self, parent: etree.Element, blocks: List[str]) -> None: ...

