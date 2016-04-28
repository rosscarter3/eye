#!/usr/bin/env python
""" applies corrections generated from segcor.py.
    View README.md for details
"""

import os, sys, argparse
import re

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from segmentation import rgb2id_array, id2mask_array

class Corrector(object):
    """Image Corrector"""
    def __init__(self,image,corr_file):
        self.image = image
        self.corr_file = corr_file

        img = Image.open(self.image)
        self.im_arr = np.array(img)
        self.id_arr = rgb2id_array(self.im_arr)

        im_name = os.path.basename(self.image)
        im_path = os.path.dirname(self.image)
        corr_name = os.path.basename(self.corr_file)[7:-4]
        outname = "{}_corrected_bs_{}.png".format(im_name,corr_name)
        self.outpath = os.path.join(im_path,outname)

    def apply_correction(self):
        """turns cell2 to colour of cell1"""
        mask, color = self.return_mask_and_color()
        self.im_arr[mask] = color
        
    def read_and_sort_corrections(self):
        corrections = []
        with open(self.corr_file, "r") as cf:
            for line in cf.readlines():
                tmp = line.split(",")
                larger_cid = max(int(tmp[0]), int(tmp[1]))
                smaller_cid = min(int(tmp[0]), int(tmp[1]))
                corrections.append([larger_cid, smaller_cid])
                
        corrections = sorted(corrections, key=lambda correction: correction[0])
        corrections.reverse()
        self.corrections = corrections

    def correct_image(self):
        """reads merges file and corrects image"""
        numtemp = self.im_arr
        with open(self.corr_file, "r") as cf:
            for correction in self.corrections:
                self.cell_id1 = correction[0]
                self.cell_id2 = correction[1]
                print correction[0], " --> ", correction[1]
                self.apply_correction()

    def save_image(self):
        """saves image"""
        Image.fromarray(self.im_arr).save(self.outpath)
        
    def return_mask_and_color(self):
        """Return mask array."""
        mask = np.zeros(self.id_arr.shape, dtype=bool)
        array_coords_cid2 = np.where(self.id_arr == self.cell_id2)
        mask[array_coords_cid2] = True
        
        array_coords_cid1 = np.where(self.id_arr == self.cell_id1)
        #print array_coords_cid1
        color = self.im_arr[array_coords_cid1]
        print color[0]
        return mask, color[0]

def parse_line(string):
    """parses lines from read merges file"""
    [x.strip() for x in string.split(',')]

    return string[0], string[1]
    
def make_mask(cid_array, cid):
    """makes mask for changing cell colours"""

    #~ mask = np.zeros(cid_array.shape, dtype=bool)
    #~ print cid_array
    #~ mask[np.where(cid_array == cid)] = True
    return id2mask_array(cid_array, cid)


    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("corr", help="Corrections File")

    args = parser.parse_args()

    corretor = Corrector(args.seg_im,args.corr)
    corretor.read_and_sort_corrections()
    corretor.correct_image()
    corretor.save_image()
    

