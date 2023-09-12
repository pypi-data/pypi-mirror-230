from math import cos, asin, atan, pi, sin, sqrt


class Polarization:
    def __init__(self):
        self._s1 = 1
        self._s2 = 0
        self._s3 = 0

    @property
    def phi(self):
        s1_new = self._s1

        if s1_new == -1 and self.s2 == 0:
            return 90

        if self.s1 == 0:
            s1_new += 0.000000001

        angle = (180/pi)*atan(self._s2/s1_new)/2

        if angle < 0:
            return angle + 90

        return angle

    @phi.setter
    def phi(self, phi):
        self._s1 = self.compute_s1(phi, self.chi)
        self._s2 = self.compute_s2(phi, self.chi)

    @property
    def chi(self):
        if self._s3 > 1:
            return 45

        if self._s3 < -1:
            return -45

        return (180/pi)*asin(self._s3)/2

    @chi.setter
    def chi(self, chi):
        self._s1 = self.compute_s1(self.phi, chi)
        self._s2 = self.compute_s2(self.phi, chi)
        self._s3 = sin(2*chi*pi/180)

    @staticmethod
    def compute_s1(phi, chi):
        return cos(2*phi*pi/180)*cos(2*chi*pi/180)

    @staticmethod
    def compute_s2(phi, chi):
        return sin(2*phi*pi/180)*cos(2*chi*pi/180)

    @property
    def s1(self):
        return self._s1

    @s1.setter
    def s1(self, s1):
        self._s1 = s1

    @property
    def s2(self):
        return self._s2

    @s2.setter
    def s2(self, s2):
        self._s2 = s2

    @property
    def s3(self):
        return self._s3

    @s3.setter
    def s3(self, s3):
        self._s3 = s3

    @property
    def polarization_fraction(self):
        return sqrt(self._s1*self._s1 + self._s2*self._s2 + self._s3*self._s3)

