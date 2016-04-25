#!/usr/bin/env python
"""Segmentation correction tool version 2.
    View README.md for details"""
# import os
import os.path
# import operator
import argparse
# import re
import datetime as dt

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from segmentation import Segmentation


def main():
    """main script function for segmentation correction"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seg_im", help="Segmented Image")
    parser.add_argument("base_im", help="Base Image")

    args = parser.parse_args()

    directory = os.path.commonprefix([args.seg_im, args.base_im])
    
    merges_file_name = return_merges_file_path(args.seg_im)

    rgb_im = Image.open(args.seg_im)
    intensity_im = Image.open(args.base_im)

    rgb_ar = np.array(rgb_im)
    intensity_ar = np.array(intensity_im)

    seg = Segmentation(rgb_ar, intensity_ar)

    # score_list.sort()

    end = int(len(seg.sorted_boundary_list)/5)
    # end = 500
    i = 0
    for boundary in seg.sorted_boundary_list[0:end]:
        i += 1
        percentage = float(i)/float(end) * 100
        cell1_id = boundary[1][0]
        cell2_id = boundary[1][1]
        merger(seg, cell1_id, cell2_id, percentage, merges_file_name)

    return 0

def return_merges_file_path(seg_im):
    
    date_time_string = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    
    name = 'merges_' + date_time_string +  '.txt'
    
    return os.path.join(os.path.dirname(seg_im), name)
    
    

def return_cell_coordinates(seg, cell_id):
    """ returns the bounding box of the cell 'cell_id' """
    array_coords = np.where(seg.id_ar == cell_id)
    y_top = min(array_coords[0])
    y_bottom = max(array_coords[0])
    x_left = min(array_coords[1])
    x_right = max(array_coords[1])

    return y_top, y_bottom, x_left, x_right


# def plot_cell(seg, cell_id):

    # ytop, ybottom, xleft, xright = return_cell_coordinates(seg, cell_id)
    # #segmentation.eval_segmentation()
    # f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    # ax1.imshow(seg.intensity_ar[ytop:ybottom, xleft:xright], cmap='Greys_r')
    # ax1.set_title('Intensity Image')
    # ax2.imshow(seg.id_ar[ytop:ybottom, xleft:xright])
    # ax2.set_title('Segmented Image')
    # ax3.imshow(seg.perimeter_array[ytop:ybottom, xleft:xright])
    # ax3.set_title('Segmentation Quality')

    # plt.show()


def merger(seg, cell_id1, cell_id2, percentage, merges_name):
    """plots the correction window for the two cells described
    by cell_id1 and cell_id2"""
    plt.switch_backend('TkAgg')

    ytop1, ybottom1, xleft1, xright1 = return_cell_coordinates(seg, cell_id1)
    ytop2, ybottom2, xleft2, xright2 = return_cell_coordinates(seg, cell_id2)

    ytop, ybottom = min(ytop1, ytop2), max(ybottom1, ybottom2)
    xleft, xright = min(xleft1, xleft2), max(xright1, xright2)

    mask = return_cell_masks(seg, cell_id1, cell_id2)
    
    labels = 'Complete', 'Incomplete'
    sizes = [percentage, 100-percentage]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.imshow(seg.intensity_ar[ytop:ybottom, xleft:xright],
               cmap='Greys_r', alpha=1)
    ax1.imshow(mask, alpha=0.5)
    ax1.set_title('Suggested Merge')
    ax2.imshow(seg.id_ar[ytop:ybottom, xleft:xright])
    ax2.set_title('Segmented Image')
    ax3.imshow(seg.perimeter_array[ytop:ybottom, xleft:xright])
    ax3.set_title('Segmentation Quality')
    ax4.pie(sizes, labels=labels,
            autopct='%1.1f%%', shadow=True)
    ax4.set_title('Correction Progress...')
    ax4.axis('equal')
    
    directory = os.path.dirname(merges_name)
    
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())

    def on_key(event):
        """ matplotlib event handler """
        # print('you pressed', event.key)
        if event.key == 'y':
            print 'merging cells'
            #seg.merge(cell_id1,cell_id2)
            write_merge(merges_name, cell_id1, cell_id2)
            seg.write_rgb_image(directory + '.png')
            plt.close()
        if event.key == 'n':
            plt.close()

    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show()

def write_merge(file_path, cid1, cid2):
    
    outstring = str(cid1)+ ' -> ' + str(cid2)
    
    with open(file_path, "a") as file_handle:
            file_handle.write(outstring)

def return_cell_masks(segmentation, cell_id1, cell_id2):
    """ returns a comibined cell mask for cell with id cell_id1
    and cell with id cell_id2 for plotting"""

    points1 = np.where(segmentation.id_ar == cell_id1)
    points2 = np.where(segmentation.id_ar == cell_id2)

    ymax = max(max(points1[0]), max(points2[0]))
    ymin = min(min(points1[0]), min(points2[0]))
    xmax = max(max(points1[1]), max(points2[1]))
    xmin = min(min(points1[1]), min(points2[1]))

    cell_mask = np.in1d(segmentation.id_ar[ymin:ymax, xmin:xmax],
                        [cell_id1, cell_id2]).reshape([ymax - ymin,
                                                       xmax - xmin])

    return cell_mask


if __name__ == "__main__":

    main()
