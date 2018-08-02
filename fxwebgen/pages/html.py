# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from io import BytesIO
from typing import Optional

from markdown.util import etree

from fxwebgen.pages.base import Page


class HtmlPage(Page):
    def process(self) -> None:
        meta = self.metadata
        with open(self.path) as fh:
            data = fh.read()

        html = etree.fromstring(data)
        assert html.tag == 'html'
        head = html.find('head')
        if head:
            title = head.find('title')
            if title is not None:
                meta['title'] = title.text
            for elm in head.iter('meta'):
                meta[elm.attrib['name']] = elm.attrib['content']
        body: Optional[etree.Element] = html.find('body')
        assert body
        html.remove(body)
        buffer = BytesIO()
        etree.ElementTree(body).write(buffer, encoding='utf-8', xml_declaration=False)
        self.body = buffer.getvalue().decode('utf-8')
