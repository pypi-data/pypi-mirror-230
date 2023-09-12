import numpy as np
from optics.geometry import Vector2D


class Vector3D(Vector2D):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

    @property
    def coords(self):
        return (self.x, self.y, self.z)

    @coords.setter
    def coords(self, xyz):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]

    def __getitem__(self, key):
        if key in ('x', 'y', 'z'):
            return self.asDict()[key]
        else:
            return self.coords.__getitem__(key)

    def __setitem__(self, key, item):
        if key == 'x':
            self.x = item
        elif key == 'y':
            self.y = item
        elif key == 'z':
            self.z = item

    def asDict(self):
        return dict(zip(list('xyz'), self.coords))

    def cross(self, other):
        x = (self[1] * other[2]) - (self[2] * other[1])
        y = (self[2] * other[0]) - (self[0] * other[2])
        z = (self[0] * other[1]) - (self[1] * other[0])
        return self.__class__(x, y, z)

    def __repr__(self):
        return 'Vector3D({}, {}, {})'.format(self.x, self.y, self.z)

    def rotate(self, angle, axes):
        length = self.magnitude
        vector = self.__class__(self.x, self.y, self.z)
        vector[axes[0]] += np.cos(angle*np.pi/180)
        vector[axes[1]] += np.sin(angle*np.pi/180)
        vector = vector.toLength(length)
        return vector
