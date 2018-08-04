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
    interlinks: StrStrDict

    def __init__(self, templater: Templater, output_dir: str, *,
                 pages_dir: Optional[str] = None,
                 static_dirs: Optional[List[str]] = None,
                 datasets_dir: Optional[str] = None,
                 datasets: Optional[StrDict] = None,
                 interlinks: Optional[StrStrDict] = None) -> None:
        self.datasets_dir = datasets_dir
        self.static_dirs = static_dirs or []
        self.templater = templater
        self.output_dir = output_dir
        self.pages_dir = pages_dir
        self.datasets = datasets or {}
        self.default_template = 'page'
        self.enable_snippets = True
        self.interlinks = interlinks or {}
