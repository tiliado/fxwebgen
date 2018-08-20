# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
import re
from typing import Any, List, Match, Optional

import markdown
from markdown.preprocessors import Preprocessor
from markdown.util import etree

from fxwebgen.context import Context
from fxwebgen.pages.base import Page


class MarkdownPage(Page):
    @classmethod
    def test(cls, path: str) -> bool:
        return path.endswith(('.md', '.mkd'))

    md: markdown.Markdown

    def __init__(self, ctx: Context, source: str, default_path: str) -> None:
        super().__init__(ctx, source, default_path[:-2] + 'html')
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
        self.md.preprocessors.add('variables', ExpandVariablesPreprocessor(self.md, ctx.global_vars), '_begin')
        self.md.preprocessors.add('snippets', SnippetsPreprocessor(self.md, ctx.snippets_dir), '_begin')

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
            for key in keys.split('.'):
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
            if value is None:
                value = '!!${ %s }' % keys if default is None else default
            return str(value)

        for i, line in enumerate(lines):
            lines[i] = self.PATTERN.sub(expand_variable, line)
        return lines


class SnippetsPreprocessor(Preprocessor):
    PATTERN = re.compile(r"(\\?){\$\s*(\w+(?:[-./]\w+)*)\s*\$}")
    snippets_dir: Optional[str]

    def __init__(self, md: markdown.Markdown, snippets_dir: Optional[str] = None) -> None:
        super().__init__(md)
        self.snippets_dir = snippets_dir

    def run(self, lines: List[str]) -> List[str]:
        def expand_variable(m: Match) -> Any:
            escape = m.group(1)
            if escape:
                return m.group(0)[1:]
            filename = m.group(2).strip().strip('/')
            if not self.snippets_dir:
                return f'\n```\nError: Snippets dir not set, "{filename}" cannot be included.\n```\n'
            path = os.path.join(self.snippets_dir, filename)
            try:
                with open(path) as fh:
                    return fh.read()
            except OSError as e:
                return f'\n```\n{e}\n```\n'

        new_lines = []
        for line in lines:
            if line:
                new_lines.extend(self.PATTERN.sub(expand_variable, line).splitlines())
            else:
                new_lines.append(line)
        return new_lines
