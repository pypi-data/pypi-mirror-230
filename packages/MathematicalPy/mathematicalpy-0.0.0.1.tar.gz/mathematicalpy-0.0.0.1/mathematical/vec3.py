import itertools
import operator

import numpy as np

from marvelous.util.typeutils import *


class Vec3:

    # --------------------------------------------------------------------------
    # Builders
    # --------------------------------------------------------------------------

    def __init__(self, x, y, z):
        # Using directly named variables and no self.__data[3]
        # array, to avoid syncing issues during named variable
        # assignment: v.x = 3 cannot update __data.
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def new(data):
        if is_iterator(data):
            data = list(itertools.islice(data, 3))
        elif not is_list(data):
            return None

        return Vec3.from_list(data)

    @staticmethod
    def from_list(ldata):
        return Vec3(ldata[0], ldata[1], ldata[2])

    @staticmethod
    def from_dict(ddata):
        keys = ddata.keys()
        values = ddata.values()
        return Vec3.from_list(keys), Vec3.from_list(values)

    @staticmethod
    def from_matrix_row(mat, row):
        return Vec3.from_list(mat[row, :])

    @staticmethod
    def from_matrix_col(mat, col):
        return Vec3.from_list(mat[:, col])

    # --------------------------------------------------------------------------
    # Casting and conversions
    # --------------------------------------------------------------------------

    def as_array(self):
        return [self.x, self.y, self.z]

    def zip(self, vec):
        return Vec3.new(zip(self.as_array(), vec.as_array()))

    def zipo(self, vec, op=operator.mul):
        """Zip two vectors applying an operator between consecutive items."""
        return Vec3.new([op(a, b) for a, b in zip(self.as_array(), vec.as_array())])

    def zipd(self, vec):
        """
        Zip two vectors to form a dictionary.

        :return:
            Dictionary with values from this vector as keys, values of other vector as values.
        """
        return dict(zip(self.as_array(), vec.as_array()))

    # --------------------------------------------------------------------------
    # Data access
    # --------------------------------------------------------------------------

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        elif i == 2:
            return self.z
        else:
            return None

    def __setitem__(self, i, value):
        if i == 0:
            self.x = value
        elif i == 1:
            self.y = value
        elif i == 2:
            self.z = value
        else:
            pass

    def __str__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    # --------------------------------------------------------------------------
    # Operators
    # --------------------------------------------------------------------------

    def cross(self, vec):
        c = np.cross(self.as_array(), vec.as_array())
        return Vec3(c[0], c[1], c[2])

    # @staticmethod
    # def cross(a, b):
    #     return a.cross(b)
