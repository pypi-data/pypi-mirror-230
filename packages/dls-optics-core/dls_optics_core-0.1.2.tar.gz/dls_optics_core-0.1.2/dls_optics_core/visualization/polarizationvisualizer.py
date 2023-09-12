import matplotlib.pyplot as plt
import numpy as np

class PolarizationVisualizer:
    def __init__(self):
        self._polarimeters = []
        self._stokes_params = []

    def plot_polarization_measurement(self):
        if not self._polarimeters:
            return

        figs = []

        for j in range(len(self._polarimeters)):
            p = self._polarimeters[j]
            params = [p.s0, p.s1, p.s2, p.s3, p.delta, p.tp, p.rp, p.ts, p.rs]

            n_primary = p.primary_angles.size
            n_secondary = p.secondary_angles_unique.size
            average_data = p.average_data
            data = p.data[:, 1, :]/p.data[:, 3, :]
            fitted_data = np.reshape(p.calculate_reflectivity(p.secondary_angles_unique, p.primary_angles, params),
                                     (n_primary, n_secondary))

            if p.primary_rotation == 'beta':
                legend_label = r'$\alpha$'
                axis_label = r'$\beta$'
            else:
                legend_label = r'$\beta$'
                axis_label = r'$\alpha$'

            fig = plt.figure(j)

            for i in range(n_secondary):
                angle1 = str(int(p.secondary_angles[i]))
                angle2 = str(int(p.secondary_angles[i + int(n_secondary)]))

                label1 = legend_label + ' = ' + angle1
                label2 = legend_label + ' = ' + angle2

                ax = fig.add_subplot(2, 2, i + 1)

                ax.plot(p.primary_angles, data[:, i], label=label1)
                ax.plot(p.primary_angles, data[:, i + int(n_secondary)], label=label2)
                ax.plot(p.primary_angles, average_data[:, i], label="Average")
                ax.plot(p.primary_angles, fitted_data[:, i],
                        label="Fit", marker="o", markerfacecolor="none", linestyle="--")

                ax.minorticks_on()
                ax.grid(which='both')

                ax.set_xlabel(r'Primary rotation ' + axis_label + r' [$^\circ$]')
                ax.set_ylabel('Intensity')
                ax.set_title('Secondary rotation ' + legend_label + ' = ' + angle1 + '/' + angle2 + r'$^\circ$')

                plt.legend()

            # plt.tight_layout()
            plt.subplots_adjust(top=0.80)

            fig.set_size_inches(15, 12)
            fig.tight_layout()

            figs.append(fig)
            
            plt.show()

        if len(figs) == 1:
            return figs[0]

        return figs

    def plot_polarization_stokes(self, x_vals, stokes_params):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x_vals, stokes_params[:, 0], label=r"$P_1$")
        ax.plot(x_vals, stokes_params[:, 1], label=r"$P_2$")
        ax.plot(x_vals, stokes_params[:, 2], label=r"$P_3$")
        ax.set_ylabel(r'Stokes-Poincar$\'{e}$ parameter $P_1$ / $P_2$ / $P_3$')
        ax.minorticks_on()
        ax.grid(which='both')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.legend()
        
        return fig, ax

    def plot_polarization_angles(self, x_vals, angles):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x_vals, angles[:, 0], label=r"$\phi$")
        ax.plot(x_vals, angles[:, 1], label=r"$\chi$")
        ax.set_ylabel(r'Angle $\phi$ / Ellipticity $\chi$')
        ax.minorticks_on()
        ax.grid(which='both')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.legend()

        return fig, ax

    @property
    def polarimeters(self):
        return self._polarimeters

    @polarimeters.setter
    def polarimeters(self, polarimeters):
        is_list = isinstance(polarimeters, list)

        if is_list:
            self._polarimeters = polarimeters
        else:
            self._polarimeters = [polarimeters]
