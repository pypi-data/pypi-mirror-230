import numpy as np
import os
import pandas as pd


class Shadow:
    @property
    def total_rays(self):
        return self._total_rays

    @property
    def good_rays(self):
        return (self.good_indices == True).sum()

    @property
    def fraction_lost(self):
        return 1 - self.good_rays/self.total_rays

    @property
    def good_indices(self):
        return np.isin(self.raw_data[:, 9], 1)

    @property
    def data(self):
        if self.ignore_lost:
            return self.raw_data[self.good_indices, :]
        else:
            return self.raw_data

    @property
    def x(self):
        return self.data[:, 0]

    @property
    def y(self):
        return self.data[:, 1]

    @property
    def z(self):
        return self.data[:, 2]

    @property
    def xp(self):
        return self.data[:, 3]

    @property
    def yp(self):
        return self.data[:, 4]

    @property
    def zp(self):
        return self.data[:, 5]

    @property
    def es_x(self):
        return self.data[:, 6]

    @property
    def es_y(self):
        return self.data[:, 7]

    @property
    def es_z(self):
        return self.data[:, 8]

    @property
    def energy(self):
        k = 1.97327e-05
        return k*self.data[:, 10]

    @property
    def index(self):
        return self.data[:, 11]

    @property
    def path_length(self):
        return self.data[:, 12]

    @property
    def es_phase(self):
        return self.data[:, 13]

    @property
    def ep_phase(self):
        return self.data[:, 14]

    @property
    def ep_x(self):
        return self.data[:, 15]

    @property
    def ep_y(self):
        return self.data[:, 16]

    @property
    def ep_z(self):
        return self.data[:, 17]

    @property
    def wavelength(self):
        return self.data[:, 18]

    @property
    def intensity(self):
        return (self.es_x*self.es_x + self.es_y*self.es_y + self.es_z*self.es_z +
                self.ep_x*self.ep_x + self.ep_y*self.ep_y + self.ep_z*self.ep_z)

    def __init__(self):
        self._total_rays = 0
        self.cols = 19
        self.ignore_lost = True
        self.raw_data = []

    def load_file(self, path):
        f = open(path, "rb")
        f.seek(24, os.SEEK_SET)

        # np.fromfile is skipping the last double for some reason so the
        # array is short by 1 entry i.e. only rays-1 long. For now we add an
        # extra dummy entry so reshaping the array doesn't fail
        tmp = np.fromfile(f, dtype=np.float64)
        tmp = np.append(tmp, [0])

        f.close()

        self._total_rays = int(len(tmp) / self.cols)

        data = np.reshape(tmp, (self._total_rays, self.cols), order='C')

        self.raw_data = data

    def to_dataframe(self):
        df = pd.DataFrame({"x": self.x,
                           "y": self.y,
                           "z": self.z,
                           "xp": self.xp,
                           "yp": self.yp,
                           "zp": self.zp,
                           "es_x": self.es_x,
                           "es_y": self.es_y,
                           "es_z": self.es_z,
                           "energy": self.energy,
                           "index": self.index,
                           "path_length": self.path_length,
                           "es_phase": self.es_phase,
                           "ep_phase": self.ep_phase,
                           "ep_x": self.ep_x,
                           "ep_y": self.ep_y,
                           "ep_z": self.ep_z,
                           "wavelength": self.wavelength})

        return df

class ShadowSlopeError(object):
    @staticmethod
    def write_dat_file(filename, data):
        f = open(filename, "w+")

        m = 0

        for x in data[:, 0]:
            if x == data[0, 0]:
                m += 1

        total = len(data[:, 0])
        n = int(total/m)

        hdr_str = "   {:d} {:d}\n"
        coord_str = "    {:11.7f}"
        val_str = "    {:11.7e}\n"
        newline = "\n"

        f.write(hdr_str.format(n, m))

        for i in range(m):
            if i > 0 and i % 5 == 0:
                f.write(newline)

            f.write(coord_str.format(data[i, 1]))

        f.write(newline)

        for i in range(total):
            if i % m == 0:
                f.write(coord_str.format(data[i, 0]))

            f.write(val_str.format(data[i, 2]))

        f.close()
