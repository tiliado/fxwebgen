# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
from typing import List, Any, Optional, Dict
import os
import shutil

from fxwebgen.pages import MarkdownPage, HtmlPage
from fxwebgen.templater import Templater
from fxwebgen.typing import StrDict


class Generator:
    output_dir: str
    templater: Templater
    pages_dir: Optional[str]
    static_dirs: List[str]
    datasets_dir: Optional[str]
    datasets: StrDict

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

    def build_page(self, source: str, path: str) -> None:
        page = MarkdownPage(source) if path.endswith('.md') else HtmlPage(source)
        page.process()
        meta = page.metadata
        meta.setdefault('title', os.path.splitext(os.path.basename(source))[0])
        meta.setdefault('template', 'page')
        path = meta.get('path', path)
        if not path.startswith('/'):
            path = '/' + path
        if not path.endswith(('/', '.html', '.htm')):
            path += '/'
        meta['path'] = meta['canonical_path'] = path
        target = self.output_dir + (path + 'index.html' if path.endswith('/') else path)
        template = meta['template']

        variables = {}
        variables.update(meta)

        variables['datasets'] = datasets = {}
        for name in meta.get('datasets', '').split(','):
            name = name.strip()
            if name:
                name = name.lower().replace(' ', '_').replace('-', '_')
                datasets[name] = self.get_dataset(name)

        snippets: Dict[str, str] = {}
        for original_name in meta.get('snippets', '').split(','):
            original_name = original_name.strip()
            normalized_name = original_name.lower().replace(' ', '_').replace('-', '_')
            if original_name and normalized_name not in snippets:
                snippets[original_name] = snippets[normalized_name] = self.templater.render(
                    [f'snippets/{normalized_name}.html'], variables)
        body = page.body or ''
        for name, content in snippets.items():
            body = body.replace(f'[Snippet: {name}]', content)
            body = body.replace(f'[snippet: {name}]', content)

        os.makedirs(os.path.dirname(target), exist_ok=True)
        variables['body'] = body
        with open(target, "wt") as fh:
            fh.write(self.templater.render([template + '.html'], variables))

    def copy_static_files(self) -> None:
        for static_dir in self.static_dirs:
            target = os.path.join(self.output_dir, os.path.basename(static_dir))
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
