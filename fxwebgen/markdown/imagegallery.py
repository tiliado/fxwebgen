# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import re
from typing import Any, List, Optional, Dict, Tuple, Pattern, cast

from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import BRK, ImagePattern
from markdown.util import etree

from fxwebgen.objects import Thumbnail

# ![alttxt](http://x.com/) or ![alttxt](<http://x.com/>)
IMAGE_LINK_RE = r'\+' + BRK + r'\s*\(\s*(<.*?>|([^"\)\s]+\s*"[^"]*"|[^\)\s]*))\s*\)'


class ImageGalleryExtension(Extension):
    def extendMarkdown(self, md: Markdown, md_globals: dict) -> None:
        md.parser.blockprocessors.add('gallery', ImageGalleryProcessor(md, md.parser), '>ulist')
        md.inlinePatterns.add('image_thumbnail_link', ImageLinkPattern(IMAGE_LINK_RE, md), '<link')


class ImageGalleryProcessor(BlockProcessor):
    RE = re.compile(r'^[+ ][Gg]allery(?:\s+\d+cols)?((?:\s*\n\+\[.+\]\(.+\|.+\))+)\s*$')
    INNER_RE = re.compile(r'^\+\[(?P<text>.+)\]\((?P<image>.+)\|(?P<params>.+)\)\s*$')

    def __init__(self, md: Markdown, *args: Any, **kwargs: Any) -> None:
        self.md = md
        super().__init__(*args, **kwargs)

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(self.RE.search(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        lines = blocks.pop(0).splitlines()
        m = re.search(r"(\d+)cols", lines[0])
        if m:
            n_cols = int(m.group(1))
            while 12 % n_cols:
                n_cols -= 1
            col_class = "col-md-%d" % (12 / n_cols)
        else:
            col_class = "col-md-4"
        del lines[0]
        gallery = etree.SubElement(parent, 'div', {"class": "gallery"})
        cointainer = etree.SubElement(gallery, 'div', {"class": "cointainer"})
        elm_row = etree.SubElement(cointainer, 'div', {"class": "thumbnails row text-center justify-content-center",
                                                       "data-toggle": "lightbox"})
        for line in lines:
            m = self.INNER_RE.match(line)
            assert m
            title = m.group("text")
            original_url = m.group("image")
            if original_url.startswith(':'):
                original_url = original_url[1:]
            else:
                print(f'Warning: Gallery image url must start with ":": "{original_url}".')

            width, height = parse_size(m.group("params"))

            thumbnail = add_thumbnail(self.md, Thumbnail(original_url, width, height))

            elm_column = etree.SubElement(elm_row, "div", {"class": col_class})
            elm_a = etree.SubElement(elm_column, "a",
                                     {"title": title, "href": ":" + original_url, "class": "thumbnail"})
            img_attr = {
                "src": ':' + thumbnail.filename,
                'class': 'img-thumbnail img-fluid',
                'alt': title,
            }
            if width:
                img_attr["width"] = str(width)
            if height:
                img_attr["height"] = str(height)
            etree.SubElement(elm_a, "img", img_attr)


class ImageLinkPattern(ImagePattern):
    def handleMatch(self, m: Pattern) -> etree.Element:
        image = super().handleMatch(m)
        thumbnail = parse_img_src_as_thumbnail(image.attrib['src'])
        if thumbnail:
            image.attrib['src'] = ":" + thumbnail.filename
            if thumbnail.style:
                image.attrib['style'] = thumbnail.style.strip()
            add_thumbnail(self.markdown, thumbnail)
            link = etree.Element('a', {
                'href': ':' + thumbnail.original_url,
                'class': 'no-gallery thumbnail',
            })
            link.append(image)
            return link
        return cast(etree.Element, image)


def parse_img_src_as_thumbnail(src: str) -> Optional[Thumbnail]:
    try:
        url, size = src.split('|')
    except ValueError:
        return None
    else:
        if url.startswith(':'):
            url = url[1:]
        else:
            print(f'Warning: Gallery image url must start with ":": "{url}".')
        width, height = parse_size(size)
        return Thumbnail(url, width, height)


def parse_size(size: str) -> Tuple[Optional[int], Optional[int]]:
    try:
        param_width, param_height = size.split("x")
    except ValueError:
        param_width, param_height = size, ''
    width: Optional[int] = int(param_width) if param_width else None
    height: Optional[int] = int(param_height) if param_height else None
    return width, height


def add_thumbnail(md: Markdown, thumbnail: Thumbnail) -> Thumbnail:
    try:
        thumbnails: Dict[str, Thumbnail] = getattr(md, 'thumbnails')
    except AttributeError:
        thumbnails = {}
        setattr(md, 'thumbnails', thumbnails)
    thumbnails[thumbnail.filename] = thumbnail
    return thumbnail


# noinspection PyPep8Naming
def makeExtension(**kwargs: Any) -> ImageGalleryExtension:  # pylint: disable=invalid-name
    return ImageGalleryExtension(**kwargs)
