# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Any, List, Match

import markdown
from markdown.preprocessors import Preprocessor
from markdown.util import etree

from fxwebgen.pages.base import Page


class MarkdownPage(Page):
    @classmethod
    def test(cls, path: str) -> bool:
        return path.endswith(('.md', '.mkd'))

    md: markdown.Markdown

    def __init__(self, source: str, default_path: str, variables: dict) -> None:
        super().__init__(source, default_path[:-2] + 'html', variables)
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
                'fxwebgen.markdown.imagegallery',
                'toc',
            ],
            lazy_ol=False)
        self.md.inlinePatterns.add('span_class', SpanWithClassPattern(SpanWithClassPattern.PATTERN), '_end')
        self.md.preprocessors.add('variables', ExpandVariablesPreprocessor(self.md, variables), '_begin')

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
        self.thumbnails.update(getattr(md, 'thumbnails', {}))


class SpanWithClassPattern(markdown.inlinepatterns.Pattern):
    PATTERN = r'\{\.\s+([-a-zA-Z_ ]+)\}'

    def handleMatch(self, m: Any) -> etree.Element:
        elm = etree.Element('span')
        elm.attrib['class'] = m.group(2)
        return elm


class ExpandVariablesPreprocessor(Preprocessor):
    PATTERN = re.compile(r"(\\?)\${(\w+(?:\.\w+)*)(?:\|(.*?))?}")

    def __init__(self, md: markdown.Markdown, variables: dict) -> None:
        super().__init__(md)
        self.variables = variables

    def run(self, lines: List[str]) -> List[str]:
        def expand_variable(m: Match) -> Any:
            escape = m.group(1)
            if escape:
                return m.group(0)[1:]
            keys = m.group(2).strip()
            default = m.group(3)
            value: Any = self.variables
            print(keys)
            for key in keys.split('.'):
                print(value, key)
                key = key.strip()
                try:
                    value = value[key]
                except (KeyError, TypeError) as e:
                    print(e)
                    try:
                        value = getattr(value, key)
                    except (AttributeError, TypeError) as e:
                        print(e)
                        value = None
                        break
                print('→', value)
            if value is None:
                value = '!!${ %s }' % keys if default is None else default
            return str(value)

        for i, line in enumerate(lines):
            lines[i] = self.PATTERN.sub(expand_variable, line)
        return lines
