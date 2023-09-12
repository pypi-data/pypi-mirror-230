from lmfit import minimize, Parameters
import numpy as np

class Plane:
    def __init__(self, a=None, b=None, c=None):
        if a is None:
            a = 0

        if b is None:
            b = 0

        if c is None:
            c = 0

        self.a = a
        self.b = b
        self.c = c

    def get_z(self, x, y, a=None, b=None, c=None):
        if a is None:
            a = self.a

        if b is None:
            b = self.b

        if c is None:
            c = self.c

        return a*x + b*y + c

    def get_y(self, x, z, a=None, b=None, c=None):
        if a is None:
            a = self.a

        if b is None:
            b = self.b

        if c is None:
            c = self.c

        return (z - c - a*x)/b

    def get_x(self, y, z, a=None, b=None, c=None):
        if a is None:
            a = self.a

        if b is None:
            b = self.b

        if c is None:
            c = self.c

        return (z - c - b*y)/a

    def get_array(self, x, y, a=None, b=None, c=None):
        if a is None:
            a = self.a

        if b is None:
            b = self.b

        if c is None:
            c = self.c

        x_len = len(x)
        result = np.zeros(x_len)

        for i in range(x_len):
            result[i] = self.get_z(x[i], y[i], a, b, c)

        return result

    def residual(self, params, x, y, data):
        a = params['a'].value
        b = params['b'].value
        c = params['c'].value

        return self.get_array(x, y, a=a, b=b, c=c) - data

    def solve_y(self, x, offset=0):
        return (offset - self.c - self.a*x)/self.b

    def fit_xyz(self, x, y, z):
        '''Fit plane to xyz data.

        Arguments:
        x -- array of x coordinates
        y -- array of y coordinates
        z -- array of z coordinates

        Returns:
        a, b, c -- coefficients of fit solution
        '''

        params = Parameters()
        params.add('a', value=self.a)
        params.add('b', value=self.b)
        params.add('c', value=self.c)

        # print('a={},b={},c={}'.format(self.a, self.b, self.c))

        fit_result = minimize(self.residual, params, args=(x, y, z))
        fit_params = fit_result.params

        self.a = fit_params.get('a').value
        self.b = fit_params.get('b').value
        self.c = fit_params.get('c').value

        return self.a, self.b, self.c
