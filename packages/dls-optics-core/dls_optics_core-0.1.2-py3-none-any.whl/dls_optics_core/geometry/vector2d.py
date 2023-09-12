import numpy as np
import numbers

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def coords(self):
        return (self.x, self.y)

    @coords.setter
    def coords(self, xyz):
        self.x = xyz[0]
        self.y = xyz[1]

    @property
    def magnitude(self):
        return np.sqrt(sum(n**2 for n in self))

    def normalized(self):
        return self * (1 / self.magnitude)

    def toLength(self, number):
        return self.normalized() * number

    def __iter__(self):
        return self.coords.__iter__()

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(*(sum(p) for p in zip(self, other)))

    def __sub__(self, other):
        return self.__add__(other*-1)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            # scalar multiplication for numbers
            return self.__class__(*((n*other) for n in self))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __getitem__(self, key):
        if key in ('x', 'y'):
            return self.asDict()[key]
        else:
            return self.coords.__getitem__(key)

    def asDict(self):
        return dict(zip(list('xy'), self.coords))

    def dot(self, other):
        return sum((p[0] * p[1]) for p in zip(self, other))

    def __repr__(self):
        return 'Vector2D({}, {})'.format(self.x, self.y)
