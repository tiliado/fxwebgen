from typing import Any

import markdown


class Extension:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def extendMarkdown(self, md: markdown.Markdown, md_globals: dict) -> None:
        pass
