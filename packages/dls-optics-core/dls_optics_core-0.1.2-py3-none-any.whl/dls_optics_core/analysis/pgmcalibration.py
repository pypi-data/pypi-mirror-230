from optics.components.pgm import PGM
from lmfit import minimize, Parameters
import numpy as np


class PGMCalibration:
    def __init__(self):
        self.pgm = PGM()
        self.e0 = 0
        self.dbeta = 0
        self.dtheta = 0

    @property
    def line_density(self):
        """Line density of grating for fitting.

        :rtype: float
        """
        return self.pgm.line_density

    @line_density.setter
    def line_density(self, val):
        self.pgm.line_density = val

    @property
    def energy(self):
        """Value of initial guess at energy (in eV) for fitting.

        :type: float
        """
        return self.pgm.energy

    @energy.setter
    def energy(self, val):
        self.pgm.energy = val

    def set_line_density(self, line_density):
        """
        .. deprecated:: 0.1
            Use :py:attr:`line_density` instead.
        """
        self.pgm.line_density = line_density

    def set_energy(self, energy):
        """
        .. deprecated:: 0.1
            Use :py:attr:`energy` instead.
        """
        self.pgm.energy = energy

    def find_offsets(self, data, holdenergy=False, holdtheta=False, holdbeta=False):
        params = Parameters()
        params.add('e0', value=self.pgm.energy)
        params.add('dtheta', value=self.dtheta)
        params.add('dbeta', value=self.dbeta)

        if holdenergy:
            params['e0'].vary = False

        if holdtheta:
            params['dtheta'].vary = False

        if holdbeta:
            params['dbeta'].vary = False

        mi = minimize(self.energy_err, params, args=(data[:, 0], data[:, 1]))

        return mi

    def energy_err(self, params, cff, y):
        parvals = params.valuesdict()
        self.pgm.energy = parvals['e0']

        fit = np.empty_like(y)

        for i in range(len(cff)):
            self.pgm.cff = cff[i]
            fit[i] = self.pgm.compute_shifted_energy(parvals['dbeta'], parvals['dtheta'])

        err = fit - y
        return err
