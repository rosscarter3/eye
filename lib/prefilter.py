#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  prefilter.py
#  
#  Copyright 2016 Ross Carter (JIC) <carterr@n108308.nbi.ac.uk>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import argparse
import os.path

import numpy as np
import PIL
from PIL import Image
import matplotlib.pyplot as plt
import skimage.measure as skim

from segmentation import rgb2id_array, id2mask_array

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")

    args = parser.parse_args()

    rgb_im = Image.open(args.seg_im)
    rgb_ar = np.array(rgb_im)
    cid_ar = rgb2id_array(rgb_ar)
    
    props = skim.regionprops(cid_ar)
    
    areas = []
    
    for cell in props:
        if cell.area > 2000:
            mask = id2mask_array(cid_ar, cell.label)
            rgb_ar[mask] = (0, 0, 0)
    
    im = PIL.Image.fromarray(rgb_ar)
    
    seg_file_path = os.path.splitext(args.seg_im)[0] + '_prefiltered.png'
    im.save(seg_file_path)
    
    
    
    
    
