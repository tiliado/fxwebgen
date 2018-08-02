from typing import List, Optional

from markdown import blockparser
from markdown.util import etree


class BlockProcessor:
    parser: blockparser.BlockParser

    def __init__(self, parser: blockparser.BlockParser) -> None:
        pass

    def test(self, parent: etree.Element, block: str) -> bool:
        pass

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        pass

    def lastChild(self, parent: etree.Element) -> Optional[etree.Element]:
        pass
