#!/usr/bin/env python
"""Segmentation correction tool, modifield from viewer.py.
    View README.md for details"""
import os
import os.path
import argparse
import re

import numpy as np
from PIL import Image
import sys

import ctypes
from sdl2 import *
from sdl2.sdlimage import IMG_LoadTexture
import sdl2.ext

import datetime as dt

from segmentation import Segmentation

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

    def update_current(self, new_path):
        """Replace the current file path with a new one."""
        self[self._current_id] = os.path.abspath(new_path)

class View(object):
    def __init__(self, wx, wy, imx, imy):
        self._zoom_level = 0
        self.windowx = wx
        self.windowy = wy
        self.imy = imy
        self.imx = imx
        self._sizes = [(wx, wy), (wx/2, wy/2), (wx/4, wy/4)]
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

    def move_left(self, step=40):
        """Shift view some steps to the left."""
        self._x -= step
        if self._x < 0:
            self._x = 0

    def move_right(self, step=40):
        """Shift view some steps to the right."""
        self._x += step
        zoom_width = self._sizes[self._zoom_level][0]
        #move_span = self.windowx - zoom_width
        move_span = self.imx - zoom_width
        if self._x > move_span:
            self._x = move_span

    def move_up(self, step=40):
        """Shift view some steps up."""
        self._y -= step
        if self._y < 0:
            self._y = 0

    def move_down(self, step=40):
        """Shift view some steps down."""
        self._y += step
        zoom_height = self._sizes[self._zoom_level][1]
        #move_span = self.windowy - zoom_height
        move_span = self.imy - zoom_height
        if self._y > move_span:
            self._y = move_span

class Viewer(object):
    """Basic viewer."""

    def __init__(self, images, segmentation, directory):
        self._images = images
        self._view = View(1536,1024,segmentation.id_ar.shape[1],segmentation.id_ar.shape[0])
        SDL_Init(SDL_INIT_VIDEO)
        self.window = SDL_CreateWindow(b"Image Viewer",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              self._view.windowx, self._view.windowy, SDL_WINDOW_SHOWN)

        self.renderer = SDL_CreateRenderer(self.window, -1, 0)
        self.display_rect = SDL_Rect(0, 0, self._view.windowx, self._view.windowy)
        self.zoom_rect = SDL_Rect(0, 0, self._view.windowx, self._view.windowy)
        self.update_image()
        self.segmentation = segmentation
        self.directory = directory
        self.fn = 'merges_{}.txt'.format( dt.datetime.now().strftime('%Y%m%d%H%M%S') )
        image_name = os.path.basename(self._images[0])
        self.im_name = '{}_corrected_{}.png'.format( image_name, dt.datetime.now().strftime('%Y%m%d%H%M%S') )
        self.fp = os.path.join(self.directory,self.fn)
        self.run()

    def update_zoom(self):
        """Update the zoom box."""
        x, y, (w, h) = self._view.current()
        self.zoom_rect = SDL_Rect(x, y, w, h)

    def update_image(self):
        """Display the next image and update the window title."""

        fpath = self._images.current()
        SDL_SetWindowTitle(self.window, b"Image Viewer: {}".format(os.path.basename(fpath)))
        texture = IMG_LoadTexture(self.renderer, fpath)

        self.update_zoom()
        SDL_RenderClear(self.renderer)
        SDL_RenderCopy(self.renderer, texture, self.zoom_rect, self.display_rect)
        SDL_RenderPresent(self.renderer)

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
        """ sets cell under the cursor to cell1"""
        x, y = ctypes.c_int(0), ctypes.c_int(0)
        buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        ix, iy = self._view.image_coordinate(x.value, y.value)

        self.c1id = self.segmentation.identifier(iy, ix)
        print "cell1 cid: ", self.c1id

    def set_cell2(self):
        """ sets cell under the cursor to cell2"""
        x, y = ctypes.c_int(0), ctypes.c_int(0)
        buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        ix, iy = self._view.image_coordinate(x.value, y.value)

        self.c2id = self.segmentation.identifier(iy, ix)
        print "cell2 cid: ", self.c2id

    def set_bcell(self):
        """ sets cell under the cursor to bcell"""
        x, y = ctypes.c_int(0), ctypes.c_int(0)
        buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        ix, iy = self._view.image_coordinate(x.value, y.value)

        self.bcid = self.segmentation.identifier(iy, ix)


    def mergecells(self,cell1id,cell2id):
        """ sets cell selected by set_cell2 to colour of cell selected by set cell 1 """
        print "Merging... "

        outstring = "%s -> %s\n"%(np.array_str(cell2id), np.array_str(cell1id))
        print outstring
        with open(self.fp, "a") as op:
            op.write(outstring)

        merge_path = os.path.join(self.directory, self.im_name)
        self.segmentation.merge(cell1id, cell2id)
        self.segmentation.write_colorful_image(merge_path)

        self._images.update_current(merge_path)
        self.update_image()

        print "Done"

    def set_to_background(self, bcid):
        """ sets cell selected by set_bcell to black """
        print "cell: ", bcid, "set to [0  0  0]"
        outstring = "%s -> [ 0, 0, 0]\n"%(np.array_str(bcid))
        with open(self.fp, "a") as op:
            op.write(outstring)

        merge_path = os.path.join(self.directory, self.im_name)
        self.segmentation.convert_to_background(bcid)
        self.segmentation.write_colorful_image(merge_path)

        self._images.update_current(merge_path)
        self.update_image()

    def run(self):
        """Run the application."""
        running = True
        event = SDL_Event()
        while running:

            keystate = SDL_GetKeyboardState(None)
            if keystate[sdl2.SDL_SCANCODE_L]:
                self.move_right()
            if keystate[sdl2.SDL_SCANCODE_H]:
                self.move_left()
            if keystate[sdl2.SDL_SCANCODE_K]:
                self.move_up()
            if keystate[sdl2.SDL_SCANCODE_J]:
                self.move_down()

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

                    if event.key.keysym.sym == sdl2.SDLK_1:
                        self.set_cell1()
                    if event.key.keysym.sym == sdl2.SDLK_2:
                        self.set_cell2()

                    if event.key.keysym.sym == sdl2.SDLK_b:
                        self.set_bcell()
                        self.set_to_background(self.bcid)

                    if event.key.keysym.sym == sdl2.SDLK_m:
                        self.mergecells(self.c1id ,self.c2id)

                if event.type == SDL_MOUSEWHEEL:
                    if event.wheel.y > 0:
                        self.zoom_in()
                    if event.wheel.y < 0:
                        self.zoom_out()

                if event.type == SDL_MOUSEBUTTONDOWN:
                    if event.button.button == SDL_BUTTON_LEFT:
                        ix, iy = self._view.image_coordinate(event.button.x, event.button.y)
                        cellid = self.segmentation.identifier(iy, ix)
                        print "x: %i, y: %i, cid: %i"%(ix, iy, cellid)

        SDL_DestroyWindow(self.window)
        sdl2.ext.quit()
        return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("base_im", help="Base Image")

    args = parser.parse_args()

    directory = os.path.commonprefix([args.seg_im, args.base_im])

    rgb_im = Image.open(args.seg_im)
    segmentation = Segmentation(np.array(rgb_im))
    colorful_fn = os.path.join(directory, 'colorful.png')
    segmentation.write_colorful_image(colorful_fn)

    images = ImageContainer()
    images.load_images(colorful_fn, args.base_im)

    viewer = Viewer(images, segmentation, directory)
    return 0

def cid_from_RGB(RGB):
    """ Generates unique ID from RGB values """
    cid = RGB[2] + 256 * RGB[1] + 256 * 256 * RGB[0]
    return int(cid)

if __name__ == "__main__":
    #import profile
    #profile.run('main()')

    main()
