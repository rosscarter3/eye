#!/usr/bin/env python
"""prefilters an image by removing cells with
a pixel area greater than 2000px"""

import argparse
import os.path

import numpy as np
import PIL
from PIL import Image
import skimage.measure as skim

from segmentation import rgb2id_array, id2mask_array


def main():
    """main run function"""
    rgb_image = Image.open(arguments.seg_im)
    rgb_array = np.array(rgb_image)
    cid_array = rgb2id_array(rgb_array)

    props = skim.regionprops(cid_array)

    for cell in props:
        if cell.area > 4000:
            mask = id2mask_array(cid_array, cell.label)
            rgb_array[mask] = (0, 0, 0)

    image = PIL.Image.fromarray(rgb_array)

    base_path = os.path.splitext(arguments.seg_im)[0]
    segmentation_file_path = base_path + '_prefiltered.png'
    image.save(segmentation_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")

    arguments = parser.parse_args()

    main()
