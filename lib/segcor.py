"""Segmentation correction tool, modifield from viewer.py"""
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

def sorted_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


class ImageContainer(list):
    def __init__(self):
        """Initialise the image file path container."""
        self._current_id = 0

    def current(self):
        """Return the current image fpath."""
        return self[self._current_id]

    def next(self):
        """Update the current image fpath to the next one."""
        self._current_id += 1
        if self._current_id >= len(self):
            self._current_id = 0

    def prev(self):
        """Update the current image fpath to the previous one."""
        self._current_id -= 1
        if self._current_id < 0:
            self._current_id = len(self) - 1

    def load_images(self, seg_im, base_im):
		"""Loads the segmented image and the base image"""
		self.append(os.path.abspath(seg_im))
		self.append(os.path.abspath(base_im))

class View(object):
    def __init__(self):
        self._zoom_level = 0
        self._sizes = [(2048, 2048), (1024, 1024), (512, 512)]
#       self._sizes = [(500, 500), (400, 400), (300, 300), (100, 100)]
        self._x = 0
        self._y = 0

    def current(self):
        """Return the current location and zoom."""
        return self._x, self._y, self._sizes[self._zoom_level]

    def _offset(self, org_size, new_size):
        """Return the zoom offset."""
        org_w, org_h = org_size
        new_w, new_h = new_size
        offset_w = (org_w - new_w) // 2
        offset_h = (org_h - new_h) // 2
        return offset_w, offset_h

    def _zoom_center(self, org_size, new_size):
        """Center view after zoom."""
        offset_w, offset_h = self._offset(org_size, new_size)
        self._x = self._x + offset_w
        self._y = self._y + offset_h
        if self._x < 0:
            self._x = 0
        if self._y < 0:
            self._y = 0

    def image_coordinate(self, wx, wy):
        """Return coordinate in image space."""
        mod_factor = self._zoom_level * 2
        if mod_factor == 0:
            return self._x + wx, self._y + wy
        ix = wx // mod_factor
        iy = wy // mod_factor

        return self._x + ix, self._y + iy

    def zoom_in(self):
        """Zoom in on center of view."""
        org_size = self._sizes[self._zoom_level]
        self._zoom_level += 1
        if self._zoom_level >= len(self._sizes):
            self._zoom_level = len(self._sizes) - 1
        new_size = self._sizes[self._zoom_level]
        self._zoom_center(org_size, new_size)

    def zoom_out(self):
        """Zoom out in on center of view."""
        org_size = self._sizes[self._zoom_level]
        self._zoom_level -= 1
        if self._zoom_level < 0:
            self._zoom_level = 0
        new_size = self._sizes[self._zoom_level]
        self._zoom_center(org_size, new_size)

    def move_left(self, step=10):
        """Shift view some steps to the left."""
        self._x -= step
        if self._x < 0:
            self._x = 0

    def move_right(self, step=10):
        """Shift view some steps to the right."""
        self._x += step
        zoom_width = self._sizes[self._zoom_level][0]
        move_span = 2048 - zoom_width
        if self._x > move_span:
            self._x = move_span

    def move_up(self, step=10):
        """Shift view some steps up."""
        self._y -= step
        if self._y < 0:
            self._y = 0

    def move_down(self, step=10):
        """Shift view some steps down."""
        self._y += step
        zoom_height = self._sizes[self._zoom_level][1]
        move_span = 2048 - zoom_height
        if self._y > move_span:
            self._y = move_span

class Viewer(object):
    """Basic viewer."""

    def __init__(self, images, numpy, directory):
        self._images = images
        self._view = View()
        SDL_Init(SDL_INIT_VIDEO)
        self.window = SDL_CreateWindow(b"Image Viewer",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              2048, 2048, SDL_WINDOW_SHOWN)

        self.renderer = SDL_CreateRenderer(self.window, -1, 0)
        self.display_rect = SDL_Rect(0, 0, 2048, 2048)
        self.zoom_rect = SDL_Rect(0, 0, 2048, 2048)
        self.update_image()
        self.numpy = numpy
	self.directory = directory
	self.fn = 'merges{}.txt'.format( dt.datetime.now().strftime('%Y%m%d%H%M%S') )
	self.fp = os.path.join(self.directory,self.fn)
        self.set_id_array()
        self.run()
	
    def update_zoom(self):
        """Update the zoom box."""
        x, y, (w, h) = self._view.current()
        self.zoom_rect = SDL_Rect(x, y, w, h)

    def update_image(self):
        """Display the next image and update the window title."""
        self.update_zoom()
        fpath = self._images.current()
        SDL_SetWindowTitle(self.window, b"Image Viewer: {}".format(os.path.basename(fpath)))
        texture = IMG_LoadTexture(self.renderer, fpath)
        SDL_RenderClear(self.renderer)
        SDL_RenderCopy(self.renderer, texture, self.zoom_rect, self.display_rect)
        SDL_RenderPresent(self.renderer)

    def set_id_array(self):
	"""Initialise numpy array of cids """
	ar = self.numpy
        id_array = np.zeros_like(ar, dtype=np.uint32)
	self.id_array = ar[:,:,2] + 256 * ar[:, :, 1] + 256 * 256 * ar[:, :, 0]

    def next(self):
        """Display the next image."""
        self._images.next()
        self.update_image()

    def prev(self):
        """Display the previous image."""
        self._images.prev()
        self.update_image()

    def zoom_in(self):
        """Zoom in on the image."""
        self._view.zoom_in()
        self.update_image()

    def zoom_out(self):
        """Zoom out from the image."""
        self._view.zoom_out()
        self.update_image()

    def move_left(self):
        """Shift the view to the left."""
        self._view.move_left()
        self.update_image()

    def move_right(self):
        """Shift the view to the right."""
        self._view.move_right()
        self.update_image()

    def move_up(self):
        """Shift the view up."""
        self._view.move_up()
        self.update_image()

    def move_down(self):
        """Shift the view down."""
        self._view.move_down()
        self.update_image()

    def set_cell1(self):
	x, y = ctypes.c_int(0), ctypes.c_int(0)
	buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
	self.cell1 = self.numpy[y.value,x.value]
	self.c1id = cid_from_RGB(self.cell1)
	print "cell1 cid: ", self.c1id

    def set_cell2(self):
	x, y = ctypes.c_int(0), ctypes.c_int(0)
	buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
	self.cell2 = self.numpy[y.value,x.value]
	self.c2id = cid_from_RGB(self.cell2)
	print "cell2 cid: ", self.c2id

    def set_bcell(self):
	x, y = ctypes.c_int(0), ctypes.c_int(0)
	buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
	self.bcell = self.numpy[y.value,x.value]
	self.bcid =  cid_from_RGB(self.bcell)
	

    def mergecells(self,cell1id,cell2id):
	print "Merging... "
	
	outstring = "%s -> %s\n"%(np.array_str(cell2id), np.array_str(cell1id))
	print outstring
	with open(self.fp, "a") as op:
	    op.write(outstring)
	
	def get_mask(array, color_index):
	    y, x, _ = self.numpy.shape
	    mask = np.zeros((y, x), dtype=bool)
	    mask[np.where(self.numpy[:,:,color_index] == cell2id[color_index])] = True
	    return mask

	red_mask = get_mask(self.numpy, 0)
	green_mask = get_mask(self.numpy, 1)
	blue_mask = get_mask(self.numpy, 2)

	mask = np.logical_and(red_mask, green_mask)
	mask = np.logical_and(mask, blue_mask)

	self.numpy[mask,:] = cell1id
	mpimg.imsave(os.path.join(self.directory,'0seg_temp.png'), self.numpy)
	    
	print "Done"

    def set_to_background(self,bcell):
	
	print "cell: ", self.bcid, "set to [0,0,0]"
	outstring = "%s -> [ 0, 0, 0]\n"%(np.array_str(self.bcell))
	with open(self.fp, "a") as op:
	    op.write(outstring)
	
	def get_mask(array, color_index):
	    y, x, _ = self.numpy.shape
	    mask = np.zeros((y, x), dtype=bool)
	    mask[np.where(self.numpy[:,:,color_index] == bcell[color_index])] = True
	    return mask

	red_mask = get_mask(self.numpy, 0)
	green_mask = get_mask(self.numpy, 1)
	blue_mask = get_mask(self.numpy, 2)

	mask = np.logical_and(red_mask, green_mask)
	mask = np.logical_and(mask, blue_mask)

	self.numpy[mask] = [0,0,0]
	    
	mpimg.imsave(os.path.join(self.directory,'0seg_temp.png'), self.numpy)

    def run(self):
        """Run the application."""
        running = True
        event = SDL_Event()
        while running:
            while SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == SDL_QUIT:
                    running = False
                    break
                if event.type == SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.next()
                    if event.key.keysym.sym == sdl2.SDLK_LEFT:
                        self.prev()
                    if event.key.keysym.sym == sdl2.SDLK_UP:
                        self.zoom_in()
                    if event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.zoom_out()
                    if event.key.keysym.sym == sdl2.SDLK_l:
                        self.move_right()
                    if event.key.keysym.sym == sdl2.SDLK_h:
                        self.move_left()
                    if event.key.keysym.sym == sdl2.SDLK_k:
                        self.move_up()
                    if event.key.keysym.sym == sdl2.SDLK_j:
                        self.move_down()

		    if event.key.keysym.sym == sdl2.SDLK_1:
                        self.set_cell1()
		    if event.key.keysym.sym == sdl2.SDLK_2:
                        self.set_cell2()

		    if event.key.keysym.sym == sdl2.SDLK_b:
                        self.set_bcell()
			self.set_to_background(self.bcell)

                    if event.key.keysym.sym == sdl2.SDLK_m:
                        self.mergecells(self.cell1,self.cell2)
			

#		    if event.key.keysym.sym == sdl2.SDLK_q:
#			running = False

                if event.type == SDL_MOUSEBUTTONDOWN:
                    if event.button.button == SDL_BUTTON_LEFT:
                        ix, iy = self._view.image_coordinate(event.button.x, event.button.y)
                        print "x: %i, y: %i, cid: "%(ix, iy)#, self.id_array[ix,iy]


        SDL_DestroyWindow(window)
        SDL_Quit()
        return 0

def cid_from_RGB(RGB):
    cid = RGB[2] + 256 * RGB[1] + 256 * 256 * RGB[0] 
    return int(cid)
    
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("seg_im", help="Segmented Image")
	parser.add_argument("base_im", help="Base Image")

	args = parser.parse_args()

	images = ImageContainer()
	images.load_images(args.seg_im, args.base_im)
	
	directory = os.path.commonprefix([args.seg_im, args.base_im])

	numpy = mpimg.imread(args.seg_im)
	
	viewer = Viewer(images,numpy,directory)

	sys.exit(viewer.run())
