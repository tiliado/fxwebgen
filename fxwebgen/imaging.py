# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from typing import Optional

from PIL import Image
from resizeimage import resizeimage


def create_thumbnail(input_file: str, output_file: str, width: Optional[int], height: Optional[int]) -> None:
    with open(input_file, 'rb') as fh:
        img = Image.open(fh)
        if width and height:
            img = resizeimage.resize_thumbnail(img, [width, height])
        elif width:
            img = resizeimage.resize_width(img, width)
        elif height:
            img = resizeimage.resize_height(img, height)
        else:
            raise ValueError('Width or height must be specified.')
        img.save(output_file)
