"""Module for generating RGB tuples for use as colors in images."""

import sys
import random
import hashlib
import itertools

def _extract_8_bits(long_value, shift=1):
    """Return an integer in the range 0, 255 by extracting 8 bits from the
    input long value. shift determines which 8 bits are taken, by default
    the first 8 bits."""

    bitmask = (1 << 8 * shift) - 1

    return (long_value & bitmask) >> (8 * (shift-1))

def _md5_hash_as_long(input_value):
    """Return the hash of the input value converted to a long."""

    hex_hash = hashlib.md5(str(input_value).encode('utf-8')).hexdigest()

    return int(hex_hash, 16)


def _generate_rgb_tuple(long_hash):
    """Return an RGB tuple with the following ranges:

    0 <= blue < 128
    128 <= green < 256
    0 <= red < 256"""

    blue = _extract_8_bits(long_hash, 1) & 127
    green = 128 + (_extract_8_bits(long_hash, 2) & 127)
    red = _extract_8_bits(long_hash, 3)

    return map(int, (red, green, blue))

def pretty_color(identifier=None):
    """Return aesthetically pleasing RGB tuple.

    :returns: RGB tuple
    """

    if identifier is None:
        try:
            identifier = random.randint(0, sys.maxint)
        except AttributeError:
            # Python3 has no sys.maxint
            identifier = random.randint(0, sys.maxsize)

    long_hash = _md5_hash_as_long(identifier)

    tuple_as_integers = _generate_rgb_tuple(long_hash)

    tuple_permutations = list(itertools.permutations(tuple_as_integers))

    selected_permutation = _extract_8_bits(long_hash, 4) % 6

    return tuple_permutations[selected_permutation]

def pretty_color_palette(identifiers, keep_zero_black=True):
    """Return dictionary with pretty colors.

    :param identifiers: set of unique identifiers
    :param keep_zero_black: whether or not the background should be black
    :returns: dictionary
    """

    color_dict = {}
    for i in identifiers:
        if keep_zero_black and i == 0:
            color_dict[0] = (0, 0, 0)
            continue
        value = pretty_color(i)
        color_dict[i] = value

    return color_dict
