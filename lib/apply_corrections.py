"""applies corrections generated from segcor.py"""
import os, sys, argparse

import numpy as np
import matplotlib.image as mpimg


def generate_cellDict(seg_im):
    ar = mpimg.imread(seg_im)
    
    y,x,_ = ar.shape
    
    id_array = np.zeros((y, x), dtype=np.uint32)
    
    id_array = ar[:,:,2] + 256 * ar[:, :, 1] + 256 * 256 * ar[:, :, 0]
    
    cell_ids = list(np.unique(id_array))
    
    for ids in range(len(cell_ids)):
	print cell_ids[ids]
    
    print cd
    pass
    
def correct_image(seg_im,celldict):
    pass
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("corr", help="Corrections File")

    args = parser.parse_args()
    
    celldict = generate_cellDict(args.seg_im)
    
    corrected_seg_im = correct_image(args.seg_im,celldict)
