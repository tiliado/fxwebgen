from typing import Union, IO, Any, Optional

class Loader:
    pass

class CLoader:
    pass

class Dumper:
    pass

class CDumper:
    pass


# noinspection PyShadowingNames
def load(stream: Union[str, IO[str]], Loader: Any =...) -> Any: ...
# noinspection PyShadowingNames
def dump(data: Any, stream: Optional[IO[str]]=..., Dumper: Any =..., **kwargs: Any) -> Optional[str]: ...
