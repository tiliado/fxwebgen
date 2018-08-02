from typing import Optional, Any

import markdown

class Pattern:
    def __init__(self, pattern: str, markdown_instance: Optional[markdown.Markdown] = None) -> None:
        pass

    def handleMatch(self, m: Any) -> markdown.util.etree.Element:
        pass
