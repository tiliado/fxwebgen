# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import TextIO, Any, IO

import yaml

Loader: Any
Dumper: Any

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def load(data: str) -> Any:
    return yaml.load(data, Loader=Loader)


def load_path(path: str) -> Any:
    with open(path) as fh:
        return load_file(fh)


def load_file(stream: TextIO) -> Any:
    return yaml.load(stream, Loader=Loader)


def dump(data: Any) -> str:
    return yaml.dump(data, Dumper=Dumper) or ''


def dump_file(stream: IO[str], data: Any) -> None:
    yaml.dump(data, stream=stream, Dumper=Dumper)
