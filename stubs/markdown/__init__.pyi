from typing import List

from markdown import util
from markdown.odict import OrderedDict
from markdown import inlinepatterns
from markdown.extensions import Extension
from .blockparser import BlockParser


class Markdown:
    inlinePatterns: OrderedDict
    references: dict
    preprocessors: OrderedDict
    parser: BlockParser

    def __init__(self,
                 extensions: List[str],
                 lazy_ol: bool) -> None:
        pass

    def convert(self, source: str) -> str:
        pass

    def registerExtension(self, extension: Extension) -> Markdown:
        pass
