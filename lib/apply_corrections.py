"""applies corrections generated from segcor.py"""
import os
import os.path
import argparse
import re

import ctypes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import ctypes
from sdl2 import *
from sdl2.sdlimage import IMG_LoadTexture
import sdl2.ext
import datetime as dt 


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("seg_im", help="Segmented Image")
	parser.add_argument("corr", help="Corrections File")

	args = parser.parse_args()

