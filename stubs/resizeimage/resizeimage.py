from typing import Union, Tuple, List
from PIL.Image import Image

def resize_width(image: Image, size: Union[int, Tuple[int, int], List[int]]) -> Image: ...
def resize_height(image: Image, size: Union[int, Tuple[int, int], List[int]]) -> Image: ...
def resize_thumbnail(image: Image, size: Union[int, Tuple[int, int], List[int]]) -> Image: ...