import numpy as np
from lmfit import minimize, Parameters
from math import cos, atan, sqrt, sin, pi, asin
from optics.beam.polarization import Polarization


class Polarimeter():
    def __init__(self, fileloader=None):
        self.data = np.empty
        self.average_data = np.empty
        self.primary_angles = np.empty
        self.secondary_angles = np.empty
        self.secondary_angles_unique = np.empty
        self.s0 = None
        self.s1 = None
        self.s2 = None
        self.s3 = None
        self.delta = None
        self.tp = None
        self.rp = None
        self.ts = None
        self.rs = None
        self._beta_primary = True
        self.file_loader = fileloader

    def load_scans(self, filenames):
        normalize_data = True

        if self.file_loader:
            first_data = self.file_loader.load_data(filenames[0])
        else:
            first_data = self.__load_txt(filenames[0])

        n_primary, n_cols = np.shape(first_data)
        n_files = len(filenames)

        if n_cols < 4:
            normalize_data = False
            n_cols += 1

        self.data = np.empty((n_primary, n_cols, n_files))

        for i in range(n_files):
            if self.file_loader:
                file_data = self.file_loader.load_data(filenames[i])
            else:
                file_data = self.__load_txt(filenames[i])

            if not normalize_data:
                shape = file_data.shape
                file_data = np.append(file_data, np.ones((shape[0], 1)), axis=1)

            # flip scan data if primary rotation went backwards
            if file_data[1, 0] < file_data[0, 0]:
                file_data = np.flipud(file_data)

            self.data[:, :, i] = file_data

        self.secondary_angles = np.zeros(n_files)
        calc_angles = np.zeros(n_files)

        for i in range(n_files):
            if self.data[0, 2, i] >= 359.5:
                self.data[:, 2, i] = 0

        # sort scan data stack in order of secondary rotation
        self.data = self.data[:, :, self.data[0, 2, :].argsort()]

        for i in range(n_files):
            angle = self.data[0, 2, i]
            self.secondary_angles[i] = round(angle, 0)
            calc_angles[i] = round(angle, 0)    

            if angle >= 180:
                calc_angles[i] = round(angle - 180, 0)

        self.secondary_angles_unique, inv = np.unique(calc_angles, return_inverse=True)
        n_secondary_unique = len(self.secondary_angles_unique)
        self.average_data = np.zeros((n_primary, n_secondary_unique))
        populated = [False]*n_secondary_unique

        for i in range(n_files):
            if populated[inv[i]]:
                self.average_data[:, inv[i]] = (self.average_data[:, inv[i]] + self.data[:, 1, i]/self.data[:, 3, i])/2
            else:
                self.average_data[:, inv[i]] = self.data[:, 1, i]/self.data[:, 3, i]
                populated[inv[i]] = True

        self.primary_angles = self.data[:, 0, 0]

    def calculate_polarization(self, s0=1, s1=1, s2=0, s3=0, delta=-45, tp=4, rp=0.001, ts=1, rs=1,
                               delta_min=-180, delta_max=180, vary_delta=True, vary_rp=True, vary_tp=True, beta_primary=True, cut_primary=0):
        self._beta_primary = beta_primary

        params = Parameters()
        params.add('s0', value=s0)
        params.add('s1', value=s1, min=-1.05, max=1.05)
        params.add('s2', value=s2, min=-1.05, max=1.05)
        params.add('s3', value=s3, min=-1.05, max=1.05)
        params.add('delta', value=delta, min=delta_min, max=delta_max)
        params.add('tp', value=tp, min=0.0001)
        params.add('rp', value=rp, min=0, max=1.02)
        params.add('ts', value=ts)
        params.add('rs', value=rs)

        params['ts'].vary = False
        params['rs'].vary = False

        params['tp'].vary = vary_tp
        params['rp'].vary = vary_rp
        params['delta'].vary = vary_delta

        if cut_primary:
            cut_data = self.average_data[:-cut_primary, :]
            cut_angles = self.primary_angles[:-cut_primary]
        else:
            cut_data = self.average_data
            cut_angles = self.primary_angles

        fitting_data = np.ravel(cut_data)

        mi = minimize(self.reflectivity_err, params, args=(self.secondary_angles_unique,
                                                           cut_angles, fitting_data))

        fit_result = mi.params.valuesdict()
        self.s0 = fit_result['s0']
        self.s1 = fit_result['s1']
        self.s2 = fit_result['s2']
        self.s3 = fit_result['s3']
        self.delta = fit_result['delta']
        self.tp = fit_result['tp']
        self.rp = fit_result['rp']
        self.ts = fit_result['ts']
        self.rs = fit_result['rs']

        return mi

    def reflectivity_err(self, params, alpha, beta, y):
        parvals = params.valuesdict()

        p = [parvals['s0'], parvals['s1'], parvals['s2'], parvals['s3'],
             parvals['delta'], parvals['tp'], parvals['rp'], parvals['ts'], parvals['rs']]

        fit = self.calculate_reflectivity(alpha, beta, p)
        err = fit - y
        return err

    def reflectivity_err_transpose(self, p, alpha, beta, y):
        fit = np.transpose(self.calculate_reflectivity(alpha, beta, p))
        err = fit - y
        return err

    def calculate_reflectivity(self, alpha, beta, p):
        s0 = p[0]
        s1 = p[1]
        s2 = p[2]
        s3 = p[3]
        delta = p[4]*pi/180
        tp = p[5]
        rp = p[6]
        ts = p[7]
        rs = p[8]

        phi_t = atan(sqrt(tp/ts))
        phi_r = atan(sqrt(rp/rs))

        alpha_rad = alpha*pi/180
        beta_rad = beta*pi/180

        n_alpha = alpha.size
        n_beta = beta.size

        reflectivity = np.empty((n_alpha*n_beta))

        for i in range(n_alpha):
            for j in range(n_beta):
                r = 1 + cos(2*phi_t)*cos(2*phi_r)*cos(2*alpha_rad[i] - 2*beta_rad[j])
                r += s1*cos(2*alpha_rad[i])*cos(2*phi_t)
                r += s1*0.5*(1 + sin(2*phi_t)*cos(delta))*cos(2*phi_r)*cos(2*beta_rad[j])
                r += s1*0.5*(1 - sin(2*phi_t)*cos(delta))*cos(2*phi_r)*cos(4*alpha_rad[i] - 2*beta_rad[j])
                r += s2*sin(2*alpha_rad[i])*cos(2*phi_t)
                r += s2*0.5*(1 + sin(2*phi_t)*cos(delta))*cos(2*phi_r)*sin(2*beta_rad[j])
                r += s2*0.5*(1 - sin(2*phi_t)*cos(delta))*cos(2*phi_r)*sin(4*alpha_rad[i] - 2*beta_rad[j])
                r += s3*sin(2*phi_t)*cos(2*phi_r)*sin(delta)*sin(2*alpha_rad[i] - 2*beta_rad[j])
                r *= s0
                reflectivity[j*n_alpha + i] = r

        return reflectivity

    @property
    def phi(self):
        p = Polarization()
        p.s1 = self.s1
        p.s2 = self.s2
        return p.phi

    @property
    def chi(self):
        p = Polarization()
        p.s1 = self.s1
        p.s2 = self.s2
        p.s3 = self.s3
        return p.chi

    @property
    def primary_rotation(self):
        return "beta" if self._beta_primary else "alpha"

    @staticmethod
    def __load_txt(filename):
        header_rows = 1
        data_found = False

        f = open(filename, 'r')

        while not data_found:
            header_rows += 1

            if '&END' in f.readline():
                data_found = True

        return np.loadtxt(filename, skiprows=header_rows)

    @property
    def polarization_fraction(self):
        p = Polarization()
        p.s1 = self.s1
        p.s2 = self.s2
        p.s3 = self.s3
        return p.polarization_fraction
