# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
from typing import List, Any, Optional, Dict, Type, ClassVar
import os
import shutil

from fxwebgen import imaging
from fxwebgen.context import Context
from fxwebgen.objects import Thumbnail
from fxwebgen.pages import MarkdownPage, HtmlPage, Page
from fxwebgen.postprocessor import PostProcessor
from fxwebgen.resources import ResourceManager


class Generator:
    ctx: Context
    post_processor: PostProcessor
    page_factories: ClassVar[List[Type[Page]]] = [MarkdownPage, HtmlPage]
    thumbnails: Dict[str, Dict[str, Thumbnail]]
    resources: ResourceManager

    def __init__(self, ctx: Context, *,
                 post_processor: Optional[PostProcessor] = None,
                 resources: Optional[ResourceManager] = None) -> None:
        self.ctx = ctx
        self.post_processor = post_processor or PostProcessor()
        self.thumbnails = {}
        self.resources = resources or ResourceManager()
        self.pages_kind = self.resources.add_kind('pages')
        self.static_files_kind = self.resources.add_kind('static_files')
        self.thumbnails_kind = self.resources.add_kind('thumbnails')

    def purge(self) -> None:
        if os.path.isdir(self.ctx.output_dir):
            shutil.rmtree(self.ctx.output_dir, ignore_errors=True)

    def build(self) -> None:
        self.before_building_pages()
        self.build_pages()
        self.after_building_pages()
        self.generate_thumbnails()
        self.copy_static_files()

    def before_building_pages(self) -> None:
        pass

    def after_building_pages(self) -> None:
        pass

    def build_pages(self) -> None:
        kind = self.pages_kind
        old_pages = {item.source: item for item in kind.resources}
        old_thumbnails = self.thumbnails
        self.thumbnails = {}
        self.resources.remove_by_kind(kind)
        assert self.ctx.pages_dir
        for root, _dirs, files in os.walk(self.ctx.pages_dir):
            for path in files:
                if path.endswith(('.md', '.html', '.html')):
                    path = os.path.join(root, path)
                    resource = old_pages.get(path)
                    if resource and resource.fresh:
                        self.thumbnails[path] = old_thumbnails.get(path, {})
                        self.resources.add(kind, resource.source, resource.target)
                    else:
                        default_path = path[len(self.ctx.pages_dir):]
                        page = self.parse_page(path, default_path)
                        self.thumbnails[page.source] = page.thumbnails
                        assert page.target
                        resource = self.resources.add(kind, page.source, page.target)
                        if not resource.fresh:
                            self.build_page(page)

    def parse_page(self, source: str, default_path: str) -> Page:
        page = self._process_source(source, default_path)
        self._process_metadata(page)
        return page

    def build_page(self, page: Page) -> Page:
        self._load_datasets_for_page(page)
        self._process_page(page)
        self._write_page(page)
        return page

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
        meta.setdefault('template', self.ctx.default_template)

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
        page.target = os.path.join(self.ctx.output_dir, page.filename)

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
        if self.ctx.enable_snippets:
            for original_name in meta.get('snippets', '').split(','):
                original_name = original_name.strip()
                normalized_name = original_name.lower().replace(' ', '_').replace('-', '_')
                if original_name and normalized_name not in snippets:
                    snippets[original_name] = snippets[normalized_name] = self.ctx.templater.render(
                        [f'snippets/{normalized_name}.html'], meta)
        meta['snippets'] = snippets

    def _process_page(self, page: Page) -> None:
        meta = page.metadata
        body = page.body or ''
        if self.ctx.enable_snippets:
            snippets: Dict[str, str] = meta['snippets']
            for name, content in snippets.items():
                body = body.replace(f'[Snippet: {name}]', content)
                body = body.replace(f'[snippet: {name}]', content)
        page.body = body
        self.post_processor.process_page(self.ctx, page)

    def _write_page(self, page: Page) -> None:
        template = page.metadata['template']
        target = page.target
        assert target
        print(f'Page: "{page.source}" → "{target}" = {page.path} {page.webroot}')
        variables = {}
        variables.update(page.metadata)
        variables['body'] = page.body
        variables['toc'] = page.toc
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wt") as fh:
            fh.write(self.ctx.templater.render(template + '.html', variables))

    def copy_static_files(self) -> None:
        kind = self.static_files_kind
        self.resources.remove_by_kind(kind)
        for static_dir in self.ctx.static_dirs:
            target_dir = os.path.join(self.ctx.output_dir, os.path.basename(static_dir))
            print(f'Dir: "{static_dir}" → "{target_dir}"')
            os.makedirs(target_dir, exist_ok=True)
            prefix_len = len(static_dir) + 1
            for source_root, dirs, files in os.walk(static_dir):
                target_root = os.path.join(target_dir, source_root[prefix_len:])
                for path in files:
                    source = os.path.join(source_root, path)
                    target = os.path.join(target_root, path)
                    resource = self.resources.add(kind, source, target)
                    if not resource.fresh:
                        shutil.copy2(source, target)
                for path in dirs:
                    target = os.path.join(target_root, path)
                    os.makedirs(target, exist_ok=True)

    def get_dataset(self, name: str) -> Any:
        try:
            return self.ctx.datasets[name]
        except KeyError:
            if self.ctx.datasets_dir:
                path = os.path.join(self.ctx.datasets_dir, name + ".json")
                with open(path) as fh:
                    dataset = json.load(fh)
            else:
                dataset = None
            self.ctx.datasets[name] = dataset
            return dataset

    def generate_thumbnails(self) -> None:
        kind = self.thumbnails_kind
        self.resources.remove_by_kind(kind)
        static_dirs = self.ctx.static_dirs
        output_dir = self.ctx.output_dir
        for thumbnails in self.thumbnails.values():
            for thumbnail in thumbnails.values():
                for static_dir in static_dirs:
                    prefix = os.path.basename(static_dir) + '/'
                    if thumbnail.original_url.startswith(prefix):
                        source = os.path.join(static_dir, thumbnail.original_url[len(prefix):])
                        target = os.path.join(output_dir, thumbnail.filename)
                        resource = self.resources.add(kind, source, target)
                        if not resource.fresh:
                            print(f'Thumbnail: {source} → {target}.')
                            imaging.create_thumbnail(source, target, thumbnail.width, thumbnail.height)
                        break
                else:
                    raise ValueError(f'Cannot find {thumbnail.original_url}.')

    def remove_stale_files(self) -> None:
        for static_dir in self.ctx.static_dirs:
            target_dir = os.path.join(self.ctx.output_dir, os.path.basename(static_dir))
            self.resources.remove_stale_files(target_dir)
