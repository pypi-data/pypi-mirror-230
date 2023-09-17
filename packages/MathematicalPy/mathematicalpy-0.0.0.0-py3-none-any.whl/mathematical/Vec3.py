import numpy as np


class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __get_data(self):
        return np.array([self.x, self.y, self.z])

    def __str__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"

    @staticmethod
    def cross(a, b):
        c = np.cross(a.__get_data(), b.__get_data())
        return Vec3(c[0], c[1], c[2])
