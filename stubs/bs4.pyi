from typing import Any, Optional

DEFAULT_OUTPUT_ENCODING: str


class ResultSet(list):
    pass


class Tag:
    def find_all(self, name: Optional[str] = None, attrs: Optional[dict] = None, recursive: bool = True,
                 text: Optional[str] = None, limit: Optional[int] = None, **kwargs: Any) -> ResultSet:
        pass

    def find(self, name: Optional[str] = None, attrs: Optional[dict] = None, recursive: bool = True,
             text: Optional[str] = None, **kwargs: Any) -> Any:
        pass


class BeautifulSoup(Tag):
    def __init__(self, markup: str = "", features: Any = None, builder: Any = None,
                 parse_only: Any = None, from_encoding: Any = None, exclude_encodings: Any = None,
                 **kwargs: Any) -> None:
        pass

    def decode(self, pretty_print: bool = False,
               eventual_encoding: str = DEFAULT_OUTPUT_ENCODING,
               formatter: str = "minimal") -> str:
        pass

