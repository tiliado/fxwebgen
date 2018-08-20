# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Any

import markdown.blockprocessors


class BlockProcessor(markdown.blockprocessors.BlockProcessor):
    md: markdown.Markdown

    def __init__(self, md: markdown.Markdown) -> None:
        super().__init__(md.parser)
        self.md = md


class Stash(list):
    def __init__(self, placeholder: str) -> None:
        super().__init__()
        self.placeholder = placeholder

    def store(self, data: Any) -> str:
        index = len(self)
        self.append(data)
        return self.placeholder % index

    def reset(self) -> None:
        self.clear()
