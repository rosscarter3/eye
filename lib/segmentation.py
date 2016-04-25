"""Module containing a segmentation class."""

import os.path
import operator

import numpy as np
import PIL.Image

from color import pretty_color_palette


def rgb2id_array(rgb_array):
    """Return identifier array."""
    return rgb_array[:, :, 2].astype(np.uint64) \
        + 256 * rgb_array[:, :, 1].astype(np.uint64) \
        + 256**2 * rgb_array[:, :, 0].astype(np.uint64)


def test_rgb2id_array():
    rgb = np.zeros((3, 3, 3), dtype=np.uint8)
    rgb[:, :, 0] = 1
    rgb[:, :, 1] = 2
    rgb[:, :, 2] = 3
    expected_id = 3 + (2 * 256) + (1 * 256**2)
    expected_ar = np.ones((3, 3), dtype=np.uint64) * expected_id
    id_ar = rgb2id_array(rgb)
    assert np.array_equal(id_ar, expected_ar), (id_ar, expected_ar)


def id2colorful_array(id_array):
    """Return a false color array."""
    output_array = np.zeros(id_array.shape + (3,), np.uint8)

    unique_identifiers = set(np.unique(id_array))

    color_dict = pretty_color_palette(
        unique_identifiers, keep_zero_black=True)

    for identifier in unique_identifiers:
        output_array[np.where(id_array == identifier)] = color_dict[identifier]

    return output_array


def test_id2colorful_array():
    id_ar = np.zeros((2, 2), dtype=np.uint64)
    id_ar[1, 1] = 1
    expected_ar = np.zeros((2, 2, 3), dtype=np.uint8)
    expected_ar[1, 1, :] = (132, 27, 117)
    colorful_ar = id2colorful_array(id_ar)
    assert np.array_equal(colorful_ar, expected_ar), (colorful_ar, expected_ar)


def id2mask_array(id_array, identifier):
    """Return mask array."""
    base_array = np.zeros(id_array.shape, dtype=bool)
    array_coords = np.where(id_array == identifier)
    base_array[array_coords] = True
    return base_array


def test_id2mask_array():
    id_ar = np.ones((2, 2), dtype=np.uint64)
    id_ar[0, 0] = 0
    expected_ar = np.ones((2, 2), dtype=bool)
    expected_ar[0, 0] = False
    mask_ar = id2mask_array(id_ar, 1)
    assert np.array_equal(mask_ar, expected_ar), (mask_ar, expected_ar)

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


class Segmentation(object):
    """A segmentation."""

    def __init__(self, rgb_ar, intensity_ar=0):
        self.rgb_ar = rgb_ar
        self.id_ar = rgb2id_array(self.rgb_ar)
        self.colorful_ar = id2colorful_array(self.id_ar)
        self.intensity_ar = intensity_ar
        self.eval_segmentation()

    def write_colorful_image(self, fpath):
        """Write false color image to disk."""
        im = PIL.Image.fromarray(self.colorful_ar)
        im.save(fpath)

    def write_rgb_image(self, fpath):
        """Write RGB image to disk.

        Where the RGB values act as identifiers originally taken from the initialisation image.
        """
        im = PIL.Image.fromarray(self.rgb_ar)
        im.save(fpath)
        
    def colourful_ar(self):
        self.colorful_ar = id2colorful_array(self.id_ar)

    def convert_to_background(self, identifier):
        """Convert a region to background."""
        mask = id2mask_array(self.id_ar, identifier)
        self.rgb_ar[mask] = (0, 0, 0)
        self.id_ar[mask] = 0
        self.colorful_ar[mask] = (0, 0, 0)

    def merge(self, id1, id2):
        """Merge two regions.

        Converts id2 values to id1 values.
        """
        mask1 = id2mask_array(self.id_ar, id1)
        mask2 = id2mask_array(self.id_ar, id2)

        # Get the rgb values.
        rgb_val = self.rgb_ar[mask1][0]
        colorful_val = self.colorful_ar[mask1][0]

        self.rgb_ar[mask2] = rgb_val
        self.colorful_ar[mask2] = colorful_val
        self.id_ar[mask2] = id1

    def identifier(self, row, col):
        """Return the identifier at position row, col."""
        return self.id_ar[row, col]

    def pretty_color(self, row, col):
        """Return the false color RGB value at position row, col."""
        return self.colorful_ar[row, col]
    
    def eval_segmentation(self):
        """evaluate the quality of the segmentation and return a list of boundaries to inspect"""
        import matplotlib.pyplot as plt
        
        print 'evaluating'
        
        cid_array = self.id_ar
        base_array = self.intensity_ar
        
        eval_array = np.zeros(cid_array.shape)
        perimeter_array = np.zeros(cid_array.shape, dtype='uint8')
        x_y_array = np.zeros(cid_array.shape)
        
        neighbour_cells_dict = dict()
        
        ele_ord = 1
        
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
                        
        for cell_id, neigh_dict in neighbour_cells_dict.iteritems():
            for neigh_id, array in neigh_dict.iteritems():
                array[1] = array[1]/array[0]
    
        for i in range(perimeter_array.shape[0]):
            for j in range(perimeter_array.shape[1]):
                if x_y_array[i,j] != 0:
                    perimeter_array[i,j] = neighbour_cells_dict[int(cid_array[i,j])][int(x_y_array[i,j])][1]
        
        self.perimeter_array = perimeter_array
        self.neighbour_cells_dict = neighbour_cells_dict
        
        neighbour_cells_dict = self.neighbour_cells_dict
    
        score_list_dict = {}
    
        for cell_id, neighbour_dict in neighbour_cells_dict.iteritems():
            for neighbour_id, p_list in neighbour_dict.iteritems():
                #print cell_id, neighbour_id, p_list
                score_list_dict[p_list[1]] = (cell_id, neighbour_id) 
    
    
        self.sorted_boundary_list = sorted(score_list_dict.items(), key=operator.itemgetter(0))
        #plt.imshow(perimeter_array, alpha=0.5)
        #plt.imshow(base_array, alpha = 0.5, cmap = 'Greys')
    
        #plt.show()

def test_background():
    def make_rgb(row):
        plane = np.array([row, row], dtype=np.uint8)
        return np.dstack([plane, plane, plane])
    rgb_ar = make_rgb([1, 2, 3])
    seg = Segmentation(rgb_ar)
    id0 = seg.identifier(0, 0)
    id1 = seg.identifier(0, 1)
    id2 = seg.identifier(0, 2)
    seg.convert_to_background(id1)
    assert np.array_equal(seg.rgb_ar, make_rgb([1, 0, 3]))
    expected_id = np.array([[id0, 0, id2],
                            [id0, 0, id2]],
                           dtype=np.uint64)
    assert np.array_equal(seg.id_ar, expected_id)

    color0 = seg.pretty_color(0, 0)
    color2 = seg.pretty_color(0, 2)
    expected_colorful = np.ones(rgb_ar.shape, dtype=np.uint8)
    expected_colorful[0:2, 0] = color0
    expected_colorful[0:2, 1] = (0, 0, 0)
    expected_colorful[0:2, 2] = color2
    assert np.array_equal(seg.colorful_ar, expected_colorful)


def test_merge():
    def make_rgb(row):
        plane = np.array([row, row], dtype=np.uint8)
        return np.dstack([plane, plane, plane])
    rgb_ar = make_rgb([1, 2, 3])
    seg = Segmentation(rgb_ar)
    id0 = seg.identifier(0, 0)
    id1 = seg.identifier(0, 1)
    id2 = seg.identifier(0, 2)
    seg.merge(id1, id2)
    assert np.array_equal(seg.rgb_ar, make_rgb([1, 2, 2]))
    assert np.array_equal(seg.id_ar,
                          np.array([[id0, id1, id1],
                                    [id0, id1, id1]],
                                   dtype=np.uint64))

    color1 = seg.pretty_color(0, 0)
    color2 = seg.pretty_color(0, 1)
    expected_colorful = np.ones(rgb_ar.shape, dtype=np.uint8)
    expected_colorful[0:2, 0] = color1
    expected_colorful[0:2, 1:3] = color2
    assert np.array_equal(seg.colorful_ar, expected_colorful)

if __name__ == "__main__":
    HERE = os.path.dirname(os.path.realpath(__file__))
    fpath = os.path.join(HERE, "..", "example_data", "00000.png")
    rgb_ar = np.array(PIL.Image.open(fpath))

    segmentation = Segmentation(rgb_ar)
    segmentation.write_colorful_image("org.png")
    identifier = segmentation.id_ar[0, 0]
    second_id = segmentation.id_ar[-1, -1]
    segmentation.merge(identifier, second_id)
    segmentation.write_colorful_image("merge.png")
    segmentation.convert_to_background(identifier)
    segmentation.write_colorful_image("background.png")
    segmentation.write_rgb_image("rgb.png")
