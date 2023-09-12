'''Module for fitting peaks in multiple data sets'''

import numpy as np
from lmfit.models import GaussianModel, LinearModel


class MultiDataPeakFitter:
    def __init__(self, model=GaussianModel()):
        self.model = model
        self.fits = []

    def get_limit_estimates(self, data, lower_offset, upper_offset): 
        n_x = len(data)
        n_y = len(data[0])

        lower_limits = np.zeros((n_x, n_y))
        upper_limits = np.zeros((n_x, n_y))

        for i in range(n_x):
            for j in range(n_y):
                max_index = np.argmax(data[i][j][:, 1])
                lower = int(max_index - lower_offset)
                upper = int(max_index + upper_offset)

                if lower < 0:
                    lower = 0

                if upper > len(data[i][j][:, 1]) - 1:
                    upper = len(data[i][j][:, 1]) - 1

                lower_limits[i, j] = int(lower)
                upper_limits[i, j] = int(upper)

        return lower_limits.astype(int), upper_limits.astype(int)

    def fit_peaks_2d(self, data, guess=None, lower_limits=None, upper_limits=None, remove_linear=False):
        self.fits = []

        model = self.model

        n_x = len(data)
        n_y = len(data[0])

        for i in range(n_x):
            tmp_fits = []

            for j in range(n_y):
                if lower_limits is None:
                    lower_limit = 0
                else:
                    lower_limit = lower_limits[i][j]

                if  upper_limits is None:
                    upper_limit = len(data[i][j]) - 1
                else:
                    upper_limit = upper_limits[i][j]

                fit_x = data[i][j][lower_limit:upper_limit, 0]
                fit_y = data[i][j][lower_limit:upper_limit, 1]

                if guess is None:
                    if remove_linear:
                        peak = self.model
                        background = LinearModel()
                        model = self.model + background
                        params = background.make_params(intercept=fit_y.min(), slope=0)
                        params += peak.guess(fit_y, x=fit_x)
                    else:
                        params = self.model.guess(fit_y, x=fit_x)

                out = model.fit(fit_y, params, x=fit_x)
                tmp_fits.append(out)

            self.fits.append(tmp_fits)

        return self.fits
