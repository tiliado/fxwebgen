# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Callable, List

from bs4 import BeautifulSoup

from fxwebgen.pages import Page


ABSOLUTE_LINK_RE = re.compile("^:.+")


def replace_absolute_links(page: Page, tree: BeautifulSoup) -> None:
    for elm in tree.find_all(href=ABSOLUTE_LINK_RE):
        elm['href'] = page.webroot + "/" + elm.get('href')[1:].lstrip('/')
    for elm in tree.find_all(src=ABSOLUTE_LINK_RE):
        elm['src'] = page.webroot + "/" + elm.get('src')[1:].lstrip('/')


class PostProcessor:
    post_processors: List[Callable[[Page, BeautifulSoup], None]]

    def __init__(self) -> None:
        self.post_processors = [replace_absolute_links]

    def process_page(self, page: Page) -> None:
        body = page.body or ''
        tree = BeautifulSoup(body, 'html.parser')
        for func in self.post_processors:
            func(page, tree)
        page.body = tree.decode()
