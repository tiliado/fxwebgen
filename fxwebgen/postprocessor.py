# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Callable, List

from bs4 import BeautifulSoup

from fxwebgen.context import Context
from fxwebgen.pages import Page


class PostProcessor:
    post_processors: List[Callable[[Context, Page, BeautifulSoup], None]]

    def __init__(self) -> None:
        self.post_processors = [
            replace_absolute_links,
            replace_pelican_links,
            replace_interlinks,
            extract_toc,
            downgrade_headings,
        ]

    def process_page(self, ctx: Context, page: Page) -> None:
        body = page.body or ''
        tree = BeautifulSoup(body, 'html.parser')
        for func in self.post_processors:
            func(ctx, page, tree)
        page.body = tree.decode()


ABSOLUTE_LINK_RE = re.compile("^:.+")


def replace_absolute_links(_ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    for attribute in 'href', 'src':
        for elm in tree.find_all(attrs={attribute: ABSOLUTE_LINK_RE}):
            elm[attribute] = page.webroot + "/" + elm.get(attribute)[1:].lstrip('/')


PELICAN_LINK_RE = re.compile(r"{filename}(\.?)(.+)\.md(.*)")


def replace_pelican_links(_ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    for link in tree.find_all(href=PELICAN_LINK_RE):
        url = link.get('href')
        print(f'Warning: {page.source}: Pelican links are deprecated: "{url}".')
        match = PELICAN_LINK_RE.search(url)
        assert match
        dot = match.group(1)
        filename = match.group(2)
        rest = match.group(3)
        if dot:
            link['href'] = dot + filename + ".html" + rest
        else:
            link['href'] = page.webroot + "/" + filename + ".html" + rest


INTERLINK_RE = re.compile("(.+?)>")


def replace_interlinks(ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    ctx.interlinks["this"] = page.webroot + "/"
    for attribute in 'href', 'src':
        for elm in tree.find_all(attrs={attribute: INTERLINK_RE}):
            url = elm.get(attribute)
            print(f'Interlink: {url}')
            m = INTERLINK_RE.search(url)
            assert m
            name = m.group(1)
            elm[attribute] = ctx.interlinks[name] + url[len(name) + 1:]


def extract_toc(_ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    toc = tree.find('div', class_='toc')
    if toc:
        toc.extract()
        page.toc = toc.decode()
    else:
        page.toc = None


def downgrade_headings(ctx: Context, _page: Page, tree: BeautifulSoup) -> None:
    if ctx.downgrade_headings:
        for i in range(5, 0, -1):
            downgraded = f'h{i + 1}'
            for elm in tree.find_all(f'h{i}'):
                elm.name = downgraded
