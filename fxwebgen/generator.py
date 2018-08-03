# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
from typing import List, Any, Optional, Dict, Type, ClassVar
import os
import shutil

from fxwebgen.pages import MarkdownPage, HtmlPage, Page
from fxwebgen.templater import Templater
from fxwebgen.typing import StrDict


# pylint: disable=too-many-instance-attributes
class Generator:
    output_dir: str
    templater: Templater
    pages_dir: Optional[str]
    static_dirs: List[str]
    datasets_dir: Optional[str]
    datasets: StrDict
    default_template: str
    enable_snippets: bool
    page_factories: ClassVar[List[Type[Page]]] = [MarkdownPage, HtmlPage]

    def __init__(self, templater: Templater, output_dir: str, *,
                 pages_dir: Optional[str] = None,
                 static_dirs: Optional[List[str]] = None,
                 datasets_dir: Optional[str] = None,
                 datasets: Optional[StrDict] = None) -> None:
        self.datasets_dir = datasets_dir
        self.static_dirs = static_dirs or []
        self.templater = templater
        self.output_dir = output_dir
        self.pages_dir = pages_dir
        self.datasets = datasets or {}
        self.default_template = 'page'
        self.enable_snippets = True

    def purge(self) -> None:
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir, ignore_errors=True)

    def build(self) -> None:
        self.before_building_pages()
        self.build_pages()
        self.after_building_pages()
        self.copy_static_files()

    def before_building_pages(self) -> None:
        pass

    def after_building_pages(self) -> None:
        pass

    def build_pages(self) -> None:
        if self.pages_dir:
            for root, _dirs, files in os.walk(self.pages_dir):
                for path in files:
                    if path.endswith(('.md', '.html', '.html')):
                        path = os.path.join(root, path)
                        target = path[len(self.pages_dir):]
                        self.build_page(path, target)

    def build_page(self, source: str, default_path: str) -> None:
        page = self._process_source(source, default_path)
        self._process_metadata(page)
        self._load_datasets_for_page(page)
        self._process_page(page)
        self._write_page(page)

    def _process_source(self, source: str, default_path: str) -> Page:
        page = None
        for factory in self.page_factories:
            if factory.test(source):
                page = factory(source, default_path)
                break
        assert page, f'No page factory for "{source}".'
        page.process()
        return page

    def _process_metadata(self, page: Page) -> None:
        meta = page.metadata
        meta.setdefault('title', os.path.splitext(os.path.basename(page.source))[0])
        meta.setdefault('template', self.default_template)

        url_deprecated = None
        if 'url' in meta:
            url_deprecated = meta['url']
            print(f'Warning: "URL: {url_deprecated}" meta directive is deprecated.')
            if not url_deprecated.startswith('/'):
                url_deprecated = '/' + url_deprecated

        save_as_deprecated = None
        if 'save_as' in meta:
            save_as_deprecated = meta['save_as']
            print(f'Warning: "save_as: {save_as_deprecated}" meta directive is deprecated.')

        path = meta.get('path', page.default_path)
        if not path.startswith('/'):
            path = '/' + path
        if not path.endswith(('/', '.html', '.htm')):
            path += '/'
        meta['path'] = path
        meta['canonical_path'] = url_deprecated or path

        if save_as_deprecated:
            filename = save_as_deprecated
        else:
            filename = (path + 'index.html' if path.endswith('/') else path)[1:]
        root = ('../' * filename.count('/')).rstrip('/') or '.'
        meta['filename'] = filename
        meta['webroot'] = root

    def _load_datasets_for_page(self, page: Page) -> None:
        meta = page.metadata

        datasets = {}
        for name in meta.get('datasets', '').split(','):
            name = name.strip()
            if name:
                name = name.lower().replace(' ', '_').replace('-', '_')
                datasets[name] = self.get_dataset(name)
        meta['datasets'] = datasets

        snippets: Dict[str, str] = {}
        if self.enable_snippets:
            for original_name in meta.get('snippets', '').split(','):
                original_name = original_name.strip()
                normalized_name = original_name.lower().replace(' ', '_').replace('-', '_')
                if original_name and normalized_name not in snippets:
                    snippets[original_name] = snippets[normalized_name] = self.templater.render(
                        [f'snippets/{normalized_name}.html'], meta)
        meta['snippets'] = snippets

    def _process_page(self, page: Page) -> None:
        meta = page.metadata
        body = page.body or ''
        if self.enable_snippets:
            snippets: Dict[str, str] = meta['snippets']
            for name, content in snippets.items():
                body = body.replace(f'[Snippet: {name}]', content)
                body = body.replace(f'[snippet: {name}]', content)
        page.body = body

    def _write_page(self, page: Page) -> None:
        template = page.metadata['template']
        target = os.path.join(self.output_dir, page.filename)
        print(f'Page: "{page.source}" → "{target}" = {page.path} {page.webroot}')
        variables = {}
        variables.update(page.metadata)
        variables['body'] = page.body
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wt") as fh:
            fh.write(self.templater.render(template + '.html', variables))

    def copy_static_files(self) -> None:
        for static_dir in self.static_dirs:
            target = os.path.join(self.output_dir, os.path.basename(static_dir))
            print(f'Dir: "{static_dir}" → "{target}"')
            if os.path.isdir(target):
                shutil.rmtree(target)
            shutil.copytree(static_dir, target)

    def get_dataset(self, name: str) -> Any:
        try:
            return self.datasets[name]
        except KeyError:
            if self.datasets_dir:
                path = os.path.join(self.datasets_dir, name + ".json")
                with open(path) as fh:
                    dataset = json.load(fh)
            else:
                dataset = None
            self.datasets[name] = dataset
            return dataset
