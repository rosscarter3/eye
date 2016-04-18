#!/usr/bin/env python
"""Segmentation correction tool, modifield from viewer.py.
    View README.md for details"""
import os
import os.path
import argparse
import re

import numpy as np
from PIL import Image

import ctypes
from sdl2 import *
from sdl2.sdlimage import IMG_LoadTexture
import sdl2.ext

import datetime as dt

from segmentation import Segmentation

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("base_im", help="Base Image")

    args = parser.parse_args()

    directory = os.path.commonprefix([args.seg_im, args.base_im])

    rgb_im = Image.open(args.seg_im)
    intensity_im = Image.open(args.base_im)
    
    segmentation = Segmentation(np.array(rgb_im),np.array(intensity_im))
    colorful_fn = os.path.join(directory, 'colorful.png')
    segmentation.write_colorful_image(colorful_fn)

    images = ImageContainer()
    images.load_images(colorful_fn, args.base_im)

    Viewer(images, segmentation, directory)
    return 0


if __name__ == "__main__":
    #import profile
    #profile.run('main()')

    main()
