import re
from typing import Any, List, Optional, Dict

from markdown import Markdown
from markdown.util import etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from fxwebgen.objects import Thumbnail


class ImageGalleryExtension(Extension):
    def extendMarkdown(self, md: Markdown, md_globals: dict) -> None:
        md.parser.blockprocessors.add('gallery', ImageGalleryProcessor(md, md.parser), '>ulist')


class ImageGalleryProcessor(BlockProcessor):
    RE = re.compile(r'^[+ ][Gg]allery(?:\s+\d+cols)?((?:\s*\n\+\[.+\]\(.+\|.+\))+)\s*$')
    INNER_RE = re.compile(r'^\+\[(?P<text>.+)\]\((?P<image>.+)\|(?P<params>.+)\)\s*$')

    def __init__(self, md: Markdown, *args: Any, **kwargs: Any) -> None:
        self.md = md
        super().__init__(*args, **kwargs)

    def test(self, parent: etree.Element, block: str) -> bool:
        return bool(self.RE.search(block))

    def run(self, parent: etree.Element, blocks: List[str]) -> None:
        try:
            thumbnails: Dict[str, Thumbnail] = getattr(self.md, 'thumbnails')
        except AttributeError:
            thumbnails = {}
            setattr(self.md, 'thumbnails', thumbnails)

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
        elm_row = etree.SubElement(cointainer, 'div', {"class": "thumbnails row", "data-toggle": "lightbox"})
        for line in lines:
            m = self.INNER_RE.match(line)
            assert m
            title = m.group("text")
            original_url = m.group("image")
            if original_url.startswith(':'):
                original_url = original_url[1:]
            else:
                print(f'Warning: Gallery image url must start with ":": "{original_url}".')

            params = m.group("params")
            try:
                param_width, param_height = params.split("x")
            except ValueError:
                param_width, param_height = params, ''
            width: Optional[int] = int(param_width) if param_width else None
            height: Optional[int] = int(param_height) if param_height else None

            thumbnail = Thumbnail(original_url, width, height)
            thumbnails[thumbnail.filename] = thumbnail

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


# noinspection PyPep8Naming
def makeExtension(**kwargs: Any) -> ImageGalleryExtension:  # pylint: disable=invalid-name
    return ImageGalleryExtension(**kwargs)
