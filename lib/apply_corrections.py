"""applies corrections generated from segcor.py"""
import os, sys, argparse
import re

import numpy as np
from PIL import Image

class Corrector(object):
    """Image Corrector"""
    def __init__(self,image,corr_file):
	self.image = image
	self.corr_file = corr_file
	
	img = Image.open(self.image)
	self.im_arr = np.array(img)
	
	im_name = os.path.basename(self.image)
	im_path = os.path.dirname(self.image)
	corr_name = os.path.basename(self.corr_file)[7:-4]
	outname = "{}_corrected_bs_{}.png".format(im_name,corr_name)
	self.outpath = os.path.join(im_path,outname)

    def apply_correction(self):
	"""turns cell2 to colour of cell1"""
	rgb1, rgb2 = self.rgb1, self.rgb2
	mask = make_mask(self.im_arr, rgb1)
	self.im_arr[mask,:] = rgb2
    
    def correct_image(self):
	"""reads merges file and corrects image"""
	numtemp = self.im_arr
	with open(self.corr_file, "r") as cf:
	    for line in cf:
		print line
		self.rgb1, self.rgb2 = parse_line(line)
		self.apply_correction()
	
    def save_image(self):
	"""saves image"""
	Image.fromarray(self.im_arr).save(self.outpath)

def parse_line(string):
    """parses lines from read merges file"""
    rgbls = re.findall("[-+]?\d+[\.]?\d*", string)
    rgbls = [float(i) for i in rgbls]
    return rgbls[0:3], rgbls[3:6]
    
def make_mask(array, rgb):
    """makes mask for changing cell colours"""
    def get_mask(array,rgb,ci):
	y, x, _ = array.shape
	mask = np.zeros((y, x), dtype=bool)
	mask[np.where(array[:,:,ci] == rgb[ci])] = True
	return mask

    red_mask = get_mask(array,rgb, 0)
    green_mask = get_mask(array,rgb, 1)
    blue_mask = get_mask(array,rgb, 2)
	
    mask = np.logical_and(red_mask, green_mask)
    mask = np.logical_and(mask, blue_mask)
    return mask
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("corr", help="Corrections File")

    args = parser.parse_args()
    
    cor_im = Corrector(args.seg_im,args.corr)
    cor_im.correct_image()
    cor_im.save_image()
    

