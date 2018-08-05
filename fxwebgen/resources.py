# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from collections import defaultdict
from typing import Dict, List, Set

from fxwebgen.utils import file_mtime


class Resource:
    kind: 'Kind'
    source: str
    target: str

    def __init__(self, kind: 'Kind', source: str, target: str) -> None:
        self.source = source
        self.target = target
        self.kind = kind

    @property
    def fresh(self) -> bool:
        if not os.path.isfile(self.target):
            return False
        return file_mtime(self.target) >= file_mtime(self.source)

    @property
    def source_exists(self) -> bool:
        return os.path.isfile(self.source)


class Kind:
    kind: int
    name: str
    resources: Set[Resource]

    def __init__(self, kind: int, name: str) -> None:
        self.name = name
        self.kind = kind
        self.resources = set()

    def add(self, resource: Resource) -> None:
        self.resources.add(resource)

    def remove(self, resource: Resource) -> None:
        self.resources.remove(resource)
        del resource.kind

    def clear(self) -> None:
        self.resources.clear()

    def __str__(self) -> str:
        return f'[Kind: {self.kind}, {self.name}, {len(self.resources)}]'

    __repr__ = __str__


class ResourceManager:
    sources: Dict[str, Set[Resource]]
    targets: Dict[str, Resource]
    kinds: List[Kind]

    def __init__(self) -> None:
        self.sources = defaultdict(set)
        self.targets = {}
        self.kinds = []

    def add_kind(self, name: str) -> Kind:
        kind = Kind(len(self.kinds), name)
        self.kinds.append(kind)
        return kind

    def add(self, kind: Kind, source: str, target: str) -> Resource:
        resource = self.targets.get(target)
        if resource:
            if resource.source != source:
                self.sources[resource.source].remove(resource)
                resource.source = source
                self.sources[source].add(resource)
        else:
            resource = Resource(kind, source, target)
            self.sources[resource.source].add(resource)
            self.targets[resource.target] = resource
            kind.add(resource)
        return resource

    def remove(self, resource: Resource) -> None:
        self.sources[resource.source].remove(resource)
        del self.targets[resource.target]
        resource.kind.remove(resource)

    def remove_by_kind(self, kind: Kind) -> None:
        for resource in kind.resources:
            self.sources[resource.source].remove(resource)
            del self.targets[resource.target]
            del resource.kind
        kind.clear()

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
