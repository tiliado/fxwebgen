# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Callable, List

from bs4 import BeautifulSoup, Tag

from fxwebgen.context import Context
from fxwebgen.markdown import imagegallery
from fxwebgen.pages import Page


class PostProcessor:
    post_processors: List[Callable[[Context, Page, BeautifulSoup], None]]

    def __init__(self) -> None:
        self.post_processors = [
            resize_images,
            replace_absolute_links,
            replace_pelican_links,
            replace_interlinks,
            extract_toc,
            downgrade_headings,
            add_title_as_heading,
            bootstrap_admonition,
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


def add_title_as_heading(ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    if ctx.title_as_heading and tree.find('h1') is None:
        heading = Tag(name='h1')
        heading.string = page.metadata['title']
        tree.insert(0, heading)


ADMONITION_CLASS = 'admonition'
ADMONITION_TITLE_CLASS = 'admonition-title'


def bootstrap_admonition(_ctx: Context, _page: Page, tree: BeautifulSoup) -> None:
    panels = tree.find_all('div', class_=ADMONITION_CLASS)
    if panels:
        for panel in panels:
            classes = panel["class"]
            index = classes.index(ADMONITION_CLASS)
            classes[index] = 'card'
            kind = classes[index + 1]
            classes[index + 1] = "border-{}".format(kind)
            classes.append('border')
            classes.append('mb-3')

            title = panel.find("p", class_=ADMONITION_TITLE_CLASS)
            panel_contents = panel.contents[:]
            panel.clear()

            if title:
                classes = title["class"]
                try:
                    index = classes.index(ADMONITION_TITLE_CLASS)
                    classes[index] = 'card-header'
                except ValueError as e:
                    print(e)
                classes.append('bg-' + kind)
                classes.append('text-dark' if kind == 'light' else 'text-light')

                index = panel_contents.index(title)
                panel_contents = panel_contents[index + 1:]
                panel.append(title)

            body = Tag(name="div")
            body["class"] = ["card-body"]
            panel.append(body)

            for i in panel_contents:
                body.append(i)


def resize_images(_ctx: Context, page: Page, tree: BeautifulSoup) -> None:
    for elm in tree.find_all('img'):
        try:
            url, size = elm['src'].split('|')
        except ValueError:
            pass
        else:
            if url.startswith(':'):
                url = url[1:]
            else:
                print(f'Warning: Gallery image url must start with ":": "{url}".')
            width, height = imagegallery.parse_size(size)
            elm['src'] = page.webroot + "/" + imagegallery.add_thumbnail(page, url, width, height).filename
            style = ''
            if width:
                style += f'width: {width}px; max-width: 100%;'
            if height:
                style += f'height: {height}px; max-height: 100%;'
            if style:
                elm['style'] = style.strip()
