from typing import List, Optional

from markdown import util
from markdown.extensions import Extension
from .blockparser import BlockParser


class Markdown:
    inlinePatterns: util.Registry
    references: dict
    preprocessors: util.Registry
    parser: BlockParser

    def __init__(self,
                 extensions: List[str],
                 lazy_ol: bool,
                 extension_configs: Optional[dict] = None) -> None:
        pass

    def convert(self, source: str) -> str:
        pass

    def registerExtension(self, extension: Extension) -> Markdown:
        pass
