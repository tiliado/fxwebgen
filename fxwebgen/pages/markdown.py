# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
import re
from typing import Any, List, Match, Optional

import markdown
from markdown.preprocessors import Preprocessor
from markdown.util import etree

from fxwebgen import utils
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
        def expand_variable(filename: str) -> str:
            filename = filename.strip().strip('/')
            if not self.snippets_dir:
                return f'`Error: Snippets dir not set, "{filename}" cannot be included.`'
            path = os.path.join(self.snippets_dir, filename)
            try:
                with open(path) as fh:
                    return fh.read()
            except OSError as e:
                return f'`{" ".join(str(e).splitlines())}`'

        new_lines = []
        for line in lines:
            buffer: List[str] = []
            pos: int = 0
            indent: str = utils.get_indent(line)
            while True:
                begin = line.find('{$', pos)
                if begin < 0:
                    if buffer:
                        buffer.append(line[pos:])
                    break
                if begin and line[begin - 1] == '\\':
                    buffer.append(line[pos:begin - 1])
                    buffer.append('{$')
                    pos = begin + 2
                else:
                    buffer.append(line[pos:begin])
                    pos = begin + 2
                    end = line.find('$}', pos)
                    if not end:
                        buffer.append(line[begin:pos])
                    else:
                        result = expand_variable(line[pos:end].strip()).strip('\n')
                        if indent:
                            result = '\n'.join((indent + s if i else s) for i, s in enumerate(result.splitlines()))
                        buffer.append(result)
                        pos = end + 2
            if buffer:
                new_lines.extend(''.join(buffer).splitlines())
            else:
                new_lines.append(line)
        return new_lines
