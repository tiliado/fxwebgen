# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from typing import Dict

from fxwebgen.utils import file_mtime


class Resource:
    def __init__(self, source: str, target: str) -> None:
        self.source = source
        self.target = target

    @property
    def fresh(self) -> bool:
        if not os.path.isfile(self.target):
            return False
        return file_mtime(self.target) >= file_mtime(self.source)

    @property
    def source_exists(self) -> bool:
        return os.path.isfile(self.source)


class ResourceManager:
    sources: Dict[str, Resource]
    targets: Dict[str, Resource]

    def __init__(self) -> None:
        self.sources = {}
        self.targets = {}

    def add(self, source: str, target: str) -> Resource:
        resource = Resource(source, target)
        self.sources[resource.source] = resource
        self.targets[resource.target] = resource
        return resource

    def remove(self, resource: Resource) -> None:
        del self.sources[resource.source]
        del self.targets[resource.target]

    def remove_stale_files(self, target_dir: str) -> None:
        if os.path.isdir(target_dir):
            for root, dirs, files in os.walk(target_dir, topdown=False):
                for path in files:
                    target = os.path.join(root, path)
                    resource = self.targets.get(target)
                    if not resource or not resource.source_exists:
                        if resource:
                            self.remove(resource)
                        print(f'Remove: {target}')
                        os.remove(target)
                for path in dirs:
                    target = os.path.join(root, path)
                    try:
                        os.rmdir(target)
                    except OSError as e:
                        if e.errno != 39:
                            raise
