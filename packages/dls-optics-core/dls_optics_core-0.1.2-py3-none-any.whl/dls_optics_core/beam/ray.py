class Ray:
    def __init__(self, x=0, y=0, z=0, theta=0, phi=0):
        self._x = x
        self._y = y
        self._z = z
        self._theta = theta
        self._phi = phi

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, val):
        self._z = val

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, val):
        self._theta = val

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, val):
        self._phi = val
