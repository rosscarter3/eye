"""Module containing a segmentation class."""

import os.path

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


class Segmentation(object):
    """A segmentation."""

    def __init__(self, fpath):
        self.rgb_ar = np.array(PIL.Image.open(fpath))
        self.id_ar = rgb2id_array(self.rgb_ar)
        self.colorful_ar = id2colorful_array(self.id_ar)

    def write_colorful_image(self, fpath):
        """Write false color image to disk."""
        im = PIL.Image.fromarray(self.colorful_ar)
        im.save(fpath)

    def convert_to_background(self, identifier):
        """Convert a region to background."""
        mask = id2mask_array(self.id_ar, identifier)
        self.rgb_ar[mask] = (0, 0, 0)
        self.id_ar[mask] = 0
        self.colorful_ar[mask] = (0, 0, 0)


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.realpath(__file__))
    fpath = os.path.join(HERE, "..", "example_data", "00000.png")
    segmentation = Segmentation(fpath)
    identifier = segmentation.id_ar[0, 0]
    segmentation.convert_to_background(identifier)
    segmentation.write_colorful_image("tmp.png")
