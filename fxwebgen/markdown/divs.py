# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Optional, Any, List

import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.util import etree, STX, ETX

from fxwebgen.markdown.base import BlockProcessor, Stash

RE_BEGIN = re.compile(r'{(#?[-_a-zA-Z0-9]+):((?:\s*#?[-_a-zA-Z0-9]+)*)\s*}')
RE_END = re.compile(r'{:(#?[-_a-zA-Z0-9]*)}')
PLACEHOLDER = STX + "!divs:%s!" + ETX
PLACEHOLDER_RE = re.compile(PLACEHOLDER % r'([0-9]+)')


class DivsExtension(Extension):
    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.registerExtension(self)
        md.parser.blockprocessors.add('divs', DivsProcessor(md), '_begin')
        md.preprocessors.add('divs', DivsPreprocessor(md), '<html_block')


class DivsPreprocessor(Preprocessor):
    def run(self, lines: List[str]) -> List[str]:
        try:
            stash = getattr(self.markdown, 'divs_stash')
            stash.reset()
        except AttributeError:
            stash = Stash(PLACEHOLDER)
            setattr(self.markdown, 'divs_stash', stash)

        new_lines = []
        for line in lines:
            directive = line.strip()
            begin = RE_BEGIN.match(directive)
            end = RE_END.match(directive)
            new_lines.append(stash.store((begin, end)) if (begin or end) else line)
        return new_lines


class Node:
    elm: etree.Element
    name: Optional[str]

    def __init__(self, name: Optional[str], elm: etree.Element) -> None:
        self.elm = elm
        self.name = name


class DivsProcessor(BlockProcessor):
    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(PLACEHOLDER_RE.search(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        nodes = []
        node = Node(None, parent)
        unprocessed_blocks: List[str] = []
        unprocessed_lines: List[str] = []

        def parse_blocks(elm: etree.Element) -> None:
            if unprocessed_lines:
                unprocessed_blocks.append('\n'.join(unprocessed_lines))
                unprocessed_lines.clear()
            if unprocessed_blocks:
                self.parser.parseBlocks(elm, unprocessed_blocks)
                unprocessed_blocks.clear()

        def process_stash(index: int) -> Node:
            parse_blocks(node.elm)
            begin, end = getattr(self.md, 'divs_stash')[index]
            if begin:
                nodes.append(node)
                name = begin.group(1).strip()
                properties = [name] if name != 'div' else []
                properties.extend(s.strip() for s in begin.group(2).split())
                elm_id = None
                elm_classes = []
                for prop in properties:
                    if prop:
                        if prop[0] == '#':
                            elm_id = prop[1:]
                        else:
                            elm_classes.append(prop)
                attrib = {}
                if elm_id:
                    attrib['id'] = elm_id
                if elm_classes:
                    attrib['class'] = ' '.join(elm_classes)
                return Node(name, etree.SubElement(node.elm, 'div', attrib))
            if end:
                name = end.group(1).strip()
                if name and name != node.name:
                    raise ValueError(f'Node mismatch {name} != {node.name}.')
                return nodes.pop()
            return node

        for block in blocks:
            unprocessed_lines.clear()
            for line in block.splitlines():
                match = PLACEHOLDER_RE.match(line.strip())
                if match:
                    node = process_stash(index=int(match.group(1)))
                else:
                    unprocessed_lines.append(line)
            if unprocessed_lines:
                unprocessed_blocks.append('\n'.join(unprocessed_lines))
                unprocessed_lines.clear()
        parse_blocks(node.elm)
        blocks.clear()


# noinspection PyPep8Naming
def makeExtension(**kwargs: Any) -> DivsExtension:  # pylint: disable=invalid-name
    return DivsExtension(**kwargs)
