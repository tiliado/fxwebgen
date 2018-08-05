# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from typing import Optional, List

from fxwebgen.templater import Templater
from fxwebgen.typing import StrDict, StrStrDict


# pylint: disable=too-many-instance-attributes
class Context:
    output_root: str
    output_dir: str
    templater: Templater
    pages_dir: Optional[str]
    static_dirs: List[str]
    datasets_dir: Optional[str]
    datasets: StrDict
    default_template: str
    enable_snippets: bool
    downgrade_headings: bool
    title_as_heading: bool
    interlinks: StrStrDict
    path_prefix: str

    def __init__(self, templater: Templater, output_root: str, *,
                 pages_dir: Optional[str] = None,
                 static_dirs: Optional[List[str]] = None,
                 datasets_dir: Optional[str] = None,
                 datasets: Optional[StrDict] = None,
                 interlinks: Optional[StrStrDict] = None,
                 enable_snippets: bool = True,
                 downgrade_headings: bool = False,
                 title_as_heading: bool = False,
                 default_template: Optional[str] = None,
                 path_prefix: Optional[str] = None) -> None:
        self.datasets_dir = datasets_dir
        self.static_dirs = static_dirs or []
        self.templater = templater
        self.output_root = output_root
        self.pages_dir = pages_dir
        self.datasets = datasets or {}
        self.default_template = default_template or 'page'
        self.enable_snippets = enable_snippets
        self.downgrade_headings = downgrade_headings
        self.title_as_heading = title_as_heading
        self.interlinks = interlinks or {}
        self.path_prefix = path_prefix.strip('/') if path_prefix else ''
        self.output_dir = os.path.join(self.output_root, self.path_prefix)
