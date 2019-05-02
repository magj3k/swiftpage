# contains all functions that will change data permanently in the 'site' directory

import os
import colorsys as cs
from PIL import Image

supported_img_extensions = {"png": "PNG", "jpg": "JPEG", "peg": "JPEG"}

def get_img_and_resize(filepath, size='large'):
    if os.path.isfile(filepath):
        im = Image.open(filepath)
        width = im.size[0]
        height = im.size[1]

        new_size = (width, height)
        if size == 'large' and max(width, height) > 320:
            if width > height:
                new_size = (320, 320*height/width)
            elif width < height:
                new_size = (320*width/height, 320)
            else:
                new_size = (320, 320)
        elif size == 'small' and max(width, height) > 100:
            if width > height:
                new_size = (100, 100*height/width)
            elif width < height:
                new_size = (100*width/height, 100)
            else:
                new_size = (100, 100)
        elif max(width, height) > 220:
            if width > height:
                new_size = (220, 220*height/width)
            elif width < height:
                new_size = (220*width/height, 220)
            else:
                new_size = (220, 220)

        im.thumbnail(new_size, Image.ANTIALIAS)
        im.save(filepath, supported_img_extensions[filepath[-3:]])

        return im

    return None