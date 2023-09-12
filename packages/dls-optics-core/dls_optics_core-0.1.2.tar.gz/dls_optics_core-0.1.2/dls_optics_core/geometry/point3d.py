from optics.geometry import Vector3D


class Point3D(Vector3D):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def __add__(self, other):
        return Point3D(*(sum(p) for p in zip(self, other)))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Vector3D(*(sum(p) for p in zip(self, other*-1)))

    def __repr__(self):
        return 'Point3D({}, {}, {})'.format(self.x, self.y, self.z)
