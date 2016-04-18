#!/usr/bin/env python
"""evaluate the quality of a segmented image by comparing it to its base image"""
import os
import os.path
import argparse

import numpy as np
from PIL import Image
from scipy.ndimage.filters import median_filter

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

#import skimage.measure as skim
from skimage.exposure import equalize_adapthist, rescale_intensity

def rgb2id_array(rgb_array):
    """Return identifier array."""
    return rgb_array[:, :, 2].astype(np.uint64) \
        + 256 * rgb_array[:, :, 1].astype(np.uint64) \
        + 256**2 * rgb_array[:, :, 0].astype(np.uint64)
        
def structure_element(i, j, element_order):
    """ returns a structuring element of size 'element_order' """
    if element_order == 1:
        """
        [0,1,0]
        [1,1,1]
        [0,1,0]
        """
        i+= 1
        j+= 1

        return [         (i  , j+1),
                (i-1, j  ),(i  , j  ),(i+1, j  ),
                         (i  , j-1)]

    if element_order == 2:
        """
        [0,0,1,0,0]
        [0,1,1,1,0]
        [1,1,1,1,1]
        [0,1,1,1,0]
        [0,0,1,0,0]
        """
        i+= 2
        j+= 2

        return [                   (i   , j+2),
                          (i-1, j+1),(i  , j+1),(i+1, j+1),
                (i-2, j  ),(i-1, j  ),(i  , j  ),(i+1, j  ),(i+2, j   ),
                          (i-1, j-1),(i  , j-1),(i+1, j-1),
                                   (i  , j-2)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("base_im", help="Base Image")
    args = parser.parse_args()

    directory = os.path.commonprefix([args.seg_im, args.base_im])

    rgb_array = np.array(Image.open(args.seg_im))
    cid_array = rgb2id_array(rgb_array)

    base_array = np.array(Image.open(args.base_im), dtype='uint64')
    eval_array = np.zeros(cid_array.shape)
    perimeter_array = np.zeros(cid_array.shape, dtype='uint8')
    x_y_array = np.zeros(cid_array.shape)

    neighbour_cells_dict = dict()
    #cell_neigh_dict = {}
    
    ele_ord = 1

    # REMOVE LOCAL MEDIAN
    #base_array_med_filter = np.array(Image.open(args.base_im), dtype='int64')
    
    #med_ele_ord = 2
    #for i in range(cid_array.shape[0]-med_ele_ord*2):
        #for j in range(cid_array.shape[1]-med_ele_ord*2):
            #signal = list()
            #for x, y in structure_element(i, j, 2):
                #signal.append( base_array[x,y])
            #sig_sorted =  sorted(signal)
            #base_array_med_filter[i+med_ele_ord,j+med_ele_ord] -= sig_sorted[6]
            
    fprint = np.array([[0,0,1,0,0],
                       [0,1,1,1,0],
                       [1,1,1,1,1],
                       [0,1,1,1,0],
                       [0,0,1,0,0]])
            
    base_array_med_filter = median_filter(base_array, size=7, footprint=fprint, output=None, mode='reflect', cval=0.0, origin=0)
    
    base_array = rescale_intensity(base_array)
    
    #base_array_clahe = equalize_adapthist(base_array, ntiles_x=5, ntiles_y=None, clip_limit=0.01, nbins=256)
    
    base_array = base_array
    
    # RESCALE IMAGE
    
    #base_array_med_filter /= np.max(np.abs(base_array_med_filter),axis=0)
    #base_array_med_filter *= (255.0/base_array_med_filter.max())
    
    
    plt.imshow(base_array, alpha=1, cmap = 'Greys')
    #plt.imshow(base_array, alpha = 0.4, cmap = 'Greys')
    
    plt.show()

    # EVALUATE BOUNDARIES
    for i in range(cid_array.shape[0]-ele_ord*2):
        for j in range(cid_array.shape[1]-ele_ord*2):
            for x, y in structure_element(i, j, ele_ord):
                if cid_array[i+ele_ord, j+ele_ord] != cid_array[x, y]:
                    eval_array[i+ele_ord, j+ele_ord] += base_array[x, y]
                    #perimeter_matrix[cid_array[i+ele_ord, j+ele_ord],cid_array[x, y]] += 1
                    #intensity_matrix[cid_array[i+ele_ord, j+ele_ord],cid_array[x, y]] += base_array[x, y]
                    
                    cell_neigh_dict = neighbour_cells_dict.get(cid_array[i+ele_ord,j+ele_ord], dict())
                    
                    # TODO named tuple instead of list 
                    cell_neigh_dict[cid_array[x,y]] = cell_neigh_dict.get(cid_array[x,y], np.zeros((2))) + [1, (base_array[x,y]+base_array[i+ele_ord,j+ele_ord])]
                    neighbour_cells_dict[cid_array[i+ele_ord,j+ele_ord]] = cell_neigh_dict
                    #print cid_array[i+ele_ord,j+ele_ord]
                    x_y_array[i+ele_ord, j+ele_ord] = cid_array[x,y]
                    
    #for k, v in neighbour_cells_dict.iteritems():
        #print k, v
                    
    for cell_id, neigh_dict in neighbour_cells_dict.iteritems():
        for neigh_id, array in neigh_dict.iteritems():
            array[1] = array[1]/array[0]
    
    for i in range(perimeter_array.shape[0]):
        for j in range(perimeter_array.shape[1]):
            if x_y_array[i,j] != 0:
                perimeter_array[i,j] = neighbour_cells_dict[int(cid_array[i,j])][int(x_y_array[i,j])][1]
    
    
    cdict = {'red':   ((0.0,  0.0, 0.0),
                       (0.3,  1.0, 1.0),
                       (0.6,  0.0, 0.0),
                       (1.0,  0.0, 0.0)),

             'green': ((0.0,  0.0, 0.0),
                       (0.3,  0.0, 0.0),
                       (0.6,  0.0, 0.0),
                       (1.0,  1.0, 1.0)),

             'blue':  ((0.0,  0.0, 0.0),
                       (0.3,  0.0, 0.0),
                       (0.6,  0.0, 0.0),
                       (1.0,  0.0, 0.0))}
                       
    bl_red_gr = LinearSegmentedColormap('bl_red_gr', cdict)
    
    fpath = os.path.join(directory, 'seg_eval.png')
    
    
    
    im = Image.fromarray(perimeter_array)
    im.save(fpath)
    
    #plt.subplot(1,2,1)
    #plt.hist(perimeter_array.flatten(), 500, facecolor='green', alpha=0.75)
    #plt.axis([1, 300, 0, 8000])
    
    #plt.subplot(1,2,2)
    plt.imshow(perimeter_array, alpha=0.5)
    plt.imshow(base_array, alpha = 0.5, cmap = 'Greys')
    
    plt.show()

def main2():
    from segmentation import Segmentation
    
    rgb_im = Image.open('/Users/carterr/tools/eye/example_data/00000.png')
    intensity_im = Image.open('/Users/carterr/tools/eye/example_data/8DAS_AA_da1-1eod1-2.lif_2_proj-g3d.png')
    segmentation = Segmentation(np.array(rgb_im),np.array(intensity_im))
    
    segmentation.eval_segmentation()

if __name__ == "__main__":
    #import profile
    #profile.run('main()')

    main2()
