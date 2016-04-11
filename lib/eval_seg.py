#!/usr/bin/env python
"""evaluate the quality of a segmented image by comparing it to its base image"""
import os
import os.path
import argparse
import re

import numpy as np
from PIL import Image

#import ctypes
#from sdl2 import *
#from sdl2.sdlimage import IMG_LoadTexture
#import sdl2.ext

#import datetime as dt
import matplotlib.pyplot as plt

from segmentation import Segmentation

def rgb2id_array(rgb_array):
    """Return identifier array."""
    return rgb_array[:, :, 2].astype(np.uint64) \
        + 256 * rgb_array[:, :, 1].astype(np.uint64) \
        + 256**2 * rgb_array[:, :, 0].astype(np.uint64)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("base_im", help="Base Image")

    args = parser.parse_args()

    directory = os.path.commonprefix([args.seg_im, args.base_im])

    rgb_array = np.array(Image.open(args.seg_im))
    cid_array = rgb2id_array(rgb_array)
    
    def structure_element(i,j):
        """
        [0,1,0]
        [1,1,1]
        [0,1,0]
        """
        i+= 1
        j+= 1
        
        return [         (i  ,j+1),
                (i-1,j  ),(i  ,j  ),(i+1,j  ),
                         (i  ,j-1)]
        
    def structure_element_2(i,j):
        """
        [0,0,1,0,0]
        [0,1,1,1,0]
        [1,1,1,1,1]
        [0,1,1,1,0]
        [0,0,1,0,0]
        """
        i+= 2
        j+= 2
        
        return [                   (i   ,j+2),
                          (i-1,j+1),(i  ,j+1),(i+1,j+1),
                (i-2,j  ),(i-1,j  ),(i  ,j  ),(i+1,j  ),(i+2,j   ),
                          (i-1,j-1),(i  ,j-1),(i+1,j-1),
                                   (i  ,j-2)]
    
    base_array = np.array(Image.open(args.base_im))
    
    eval_array = np.zeros(cid_array.shape)
    
    for i in range(cid_array.shape[0]-4):
        for j in range(cid_array.shape[1]-4):
            for x,y in structure_element_2(i,j):
                if cid_array[i+1,j+1] != cid_array[x,y]:
                    eval_array[i+1,j+1] += base_array[x,y]

    
    plt.imshow(eval_array)
    plt.show()
            
                
    
    


if __name__ == "__main__":
    #import profile
    #profile.run('main()')

    main()
