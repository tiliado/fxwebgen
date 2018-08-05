# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Optional, List

from fxwebgen.templater import Templater
from fxwebgen.typing import StrDict, StrStrDict


# pylint: disable=too-many-instance-attributes
class Context:
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

    def __init__(self, templater: Templater, output_dir: str, *,
                 pages_dir: Optional[str] = None,
                 static_dirs: Optional[List[str]] = None,
                 datasets_dir: Optional[str] = None,
                 datasets: Optional[StrDict] = None,
                 interlinks: Optional[StrStrDict] = None,
                 enable_snippets: bool = True,
                 downgrade_headings: bool = False,
                 title_as_heading: bool = False,
                 default_template: Optional[str] = None) -> None:
        self.datasets_dir = datasets_dir
        self.static_dirs = static_dirs or []
        self.templater = templater
        self.output_dir = output_dir
        self.pages_dir = pages_dir
        self.datasets = datasets or {}
        self.default_template = default_template or 'page'
        self.enable_snippets = enable_snippets
        self.downgrade_headings = downgrade_headings
        self.title_as_heading = title_as_heading
        self.interlinks = interlinks or {}
