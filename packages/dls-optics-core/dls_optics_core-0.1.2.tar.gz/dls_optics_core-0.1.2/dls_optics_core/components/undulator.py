from math import pi, cos, sqrt, sin
from optics.beam import Polarization

class Undulator:
    def __init__(self):
        self._period = 64
        self._top_row_position = 0
        self._bottom_row_position = 0
        self._bx0 = 1
        self._by0 = 1
        self._electron_energy = 3

    @property
    def period(self):
        """Period of undulator magnets in mm."""
        return self._period

    @period.setter
    def period(self, period):
        self._period = period

    @property
    def top_row_position(self):
        """Offset of top magnet row from centre position in mm."""
        return self._top_row_position

    @top_row_position.setter
    def top_row_position(self, position):
        self._top_row_position = position

    @property
    def bottom_row_position(self):
        """Offset of bottom magnet row from centre position in mm."""
        return self._bottom_row_position

    @bottom_row_position.setter
    def bottom_row_position(self, position):
        self._bottom_row_position = position

    @property
    def top_row_phase(self):
        """Phase of magnetic field contribution from top magnet row in radians."""
        return 2*pi*self._top_row_position/self._period

    @property
    def bottom_row_phase(self):
        """Phase of magnetic field contribution from bottom magnet row in radians."""
        return 2*pi*self._bottom_row_position/self._period

    @property
    def bx0(self):
        return self._bx0

    @bx0.setter
    def bx0(self, bx0):
        self._bx0 = bx0

    @property
    def by0(self):
        return self._by0

    @by0.setter
    def by0(self, by0):
        self._by0 = by0

    @property
    def k(self):
        return 0.934*(self._period/10)*sqrt(self.bx(0)*self.bx(0) + self.by(0)*self.by(0))

    def bx(self, z):
        return self._bx0*(-2*cos(z*2*pi/self._period) +
                          cos(z*2*pi/self._period - self.top_row_phase) +
                          cos(z*2*pi/self._period - self.bottom_row_phase))

    def by(self, z):
        return self._by0*(2*cos(z*2*pi/self._period) +
                          cos(z*2*pi/self._period - self.top_row_phase) +
                          cos(z*2*pi/self._period - self.bottom_row_phase))

    @property
    def electron_energy(self):
        """Energy of storage ring electrons in GeV."""
        return self._electron_energy

    @electron_energy.setter
    def electron_energy(self, e):
        self._electron_energy = e

    @property
    def photon_energy(self):
        """Energy of photons emitted by undulator in eV."""
        return 950*self._electron_energy*self._electron_energy/((1 + (self.k*self.k/2))*self._period)

    @property
    def es(self):
        return -self.bx(0)

    @property
    def ep(self):
        return self.by(0)

    @property
    def polarization(self):
        """Polarization of light emitted by undulator."""
        ep = self.ep
        es = self.es
        phase = self.phase

        s0 = (ep*ep + es*es)/2

        p = Polarization()
        p.s1 = (ep*ep - es*es)/2/s0
        p.s2 = ep*es*cos(phase)/s0
        p.s3 = -ep*es*sin(phase)/s0

        return p

    @property
    def phase(self):
        """Net phase of undulator magnetic field."""
        return self.top_row_phase + self.bottom_row_phase