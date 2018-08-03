# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Any

import markdown
from markdown.util import etree

from fxwebgen.pages.base import Page


class MarkdownPage(Page):
    @classmethod
    def test(cls, path: str) -> bool:
        return path.endswith(('.md', '.mkd'))

    md: markdown.Markdown

    def __init__(self, source: str, default_path: str) -> None:
        super().__init__(source, default_path[:-2] + 'html')
        self.md = markdown.Markdown(
            extensions=[
                'meta',
                'sane_lists',
                'footnotes(PLACE_MARKER=$FOOTNOTES$)',
                'fenced_code',
                'codehilite',
                'def_list',
                'attr_list',
                'abbr',
                'admonition',
                'fxwebgen.markdown.bootstrap',
            ],
            lazy_ol=False)
        self.md.inlinePatterns.add('span_class', SpanWithClassPattern(SpanWithClassPattern.PATTERN), '_end')

    def process(self) -> None:
        with open(self.source) as fh:
            data = fh.read()
        md = self.md
        self.body = md.convert(data)
        m = self.metadata
        try:
            for key, val in getattr(md, 'Meta').items():
                m[key] = " ".join(val)
        except AttributeError:
            pass
        self.references = md.references


class SpanWithClassPattern(markdown.inlinepatterns.Pattern):
    PATTERN = r'\{\.\s+([-a-zA-Z_ ]+)\}'

    def handleMatch(self, m: Any) -> etree.Element:
        elm = etree.Element('span')
        elm.attrib['class'] = m.group(2)
        return elm
