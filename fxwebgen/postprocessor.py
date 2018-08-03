# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Callable, List, Optional

from bs4 import BeautifulSoup

from fxwebgen.pages import Page
from fxwebgen.typing import StrStrDict


class PostProcessor:
    interlinks: StrStrDict
    post_processors: List[Callable[['PostProcessor', Page, BeautifulSoup], None]]

    def __init__(self, interlinks: Optional[StrStrDict] = None) -> None:
        self.interlinks = interlinks or {}
        self.post_processors = [
            replace_absolute_links,
            replace_pelican_links,
            replace_interlinks,
        ]

    def process_page(self, page: Page) -> None:
        body = page.body or ''
        tree = BeautifulSoup(body, 'html.parser')
        for func in self.post_processors:
            func(self, page, tree)
        page.body = tree.decode()


ABSOLUTE_LINK_RE = re.compile("^:.+")


def replace_absolute_links(_ctx: PostProcessor, page: Page, tree: BeautifulSoup) -> None:
    for elm in tree.find_all(href=ABSOLUTE_LINK_RE):
        elm['href'] = page.webroot + "/" + elm.get('href')[1:].lstrip('/')
    for elm in tree.find_all(src=ABSOLUTE_LINK_RE):
        elm['src'] = page.webroot + "/" + elm.get('src')[1:].lstrip('/')


PELICAN_LINK_RE = re.compile(r"\{filename\}(\.?)(.+)\.md(.*)")


def replace_pelican_links(_ctx: PostProcessor, page: Page, tree: BeautifulSoup) -> None:
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


def replace_interlinks(ctx: PostProcessor, page: Page, tree: BeautifulSoup) -> None:
    ctx.interlinks["this"] = page.webroot + "/"
    for attribute in 'href', 'src':
        for elm in tree.find_all(attrs={attribute: INTERLINK_RE}):
            url = elm.get(attribute)
            print(f'Interlink: {url}')
            m = INTERLINK_RE.search(url)
            assert m
            name = m.group(1)
            elm[attribute] = ctx.interlinks[name] + url[len(name) + 1:]
