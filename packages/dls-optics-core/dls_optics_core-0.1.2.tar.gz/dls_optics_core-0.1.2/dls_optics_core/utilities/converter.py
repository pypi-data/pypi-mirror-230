h = 6.62607004e-34
c = 299792458
eV = 1.6021766208e-19


class Converter:
    @staticmethod
    def convert_energy_wavelength(value):
        return h*c/(eV*value)
