"""PGM plane grating monochromator.
"""

import numpy as np
from optics.geometry import Plane, Ray3D, Point3D
from optics.utilities import Converter
from optics.components import Grating


class PGM(object):
    """PGM plane grating monochromator.
    """
    def __init__(self, grating=Grating()):
        self._grating = grating

        self._mirror_voffset = 20
        self._mirror_hoffset = 0
        self._mirror_axis_voffset = 0
        self._mirror_axis_hoffset = 0
        self._mirror_length = 450
        self._mirror_width = 70
        self._mirror_height = 50

        self._grating_length = 150
        self._grating_width = 40
        self._grating_height = 50

        self._mirror_plane = None
        self._grating_plane = None

    # region: properties

    @property
    def cff(self):
        """Fixed-focus constant."""
        return self._grating.cff

    @cff.setter
    def cff(self, cff):
        self._grating.cff = cff

    @property
    def energy(self):
        """Energy setting of PGM in eV."""
        return self._grating.energy

    @energy.setter
    def energy(self, energy):
        self._grating.energy = energy

    @property
    def order(self):
        """Diffraction order of PGM grating."""
        return self._grating.order

    @order.setter
    def order(self, order):
        self._grating.order = order

    @property
    def line_density(self):
        """Line density of PGM grating in lines/mm."""
        return self._grating.line_density

    @line_density.setter
    def line_density(self, line_density):
        self._grating.line_density = line_density

    @property
    def beta(self):
        """Angle of PGM grating surface normal w.r.t. horizontal in degrees."""
        return self._grating.beta

    @beta.setter
    def beta(self, beta):
        alpha = 2*self.theta + beta
        self._grating.set_angles(alpha, beta)

    @property
    def alpha(self):
        """Angle of incidence on PGM grating w.r.t.
           surface normal in degrees."""
        return self._grating.alpha

    @property
    def theta(self):
        """Angle of PGM mirror surface normal w.r.t. horizontal in degrees."""
        return (self._grating.alpha - self.beta)/2

    @theta.setter
    def theta(self, theta):
        alpha = 2*theta + self._grating.beta
        self._grating.set_angles(alpha, self._grating.beta)

    @property
    def mirror_voffset(self):
        return self._mirror_voffset

    @mirror_voffset.setter
    def mirror_voffset(self, offset):
        self._mirror_voffset = offset

    @property
    def mirror_hoffset(self):
        return self._mirror_hoffset

    @mirror_hoffset.setter
    def mirror_hoffset(self, offset):
        self._mirror_hoffset = offset

    @property
    def mirror_axis_voffset(self):
        return self._mirror_axis_voffset

    @mirror_axis_voffset.setter
    def mirror_axis_voffset(self, offset):
        self._mirror_axis_voffset = offset

    @property
    def mirror_axis_hoffset(self):
        return self._mirror_axis_hoffset

    @mirror_axis_hoffset.setter
    def mirror_axis_hoffset(self, offset):
        self._mirror_axis_hoffset = offset

    @property
    def mirror_length(self):
        return self._mirror_length

    @mirror_length.setter
    def mirror_length(self, length):
        self._mirror_length = length

    @property
    def mirror_width(self):
        return self._mirror_width

    @mirror_width.setter
    def mirror_width(self, width):
        self._mirror_length = width

    @property
    def mirror_height(self):
        return self._mirror_height

    @mirror_height.setter
    def mirror_height(self, height):
        self._mirror_height = height

    @property
    def grating_length(self):
        return self._grating_length

    @grating_length.setter
    def grating_length(self, length):
        self._grating_length = length

    @property
    def grating_width(self):
        return self._grating_width

    @grating_width.setter
    def grating_width(self, width):
        self._grating_length = width

    @property
    def grating_height(self):
        return self._grating_height

    @grating_height.setter
    def grating_height(self, height):
        self._grating_height = height

    # endregion: properties

    def compute_shifted_energy(self, dbeta, dtheta):
        """Compute shifted energy observed when offsets
           in grating and mirror angles are present."""
        dalpha = 2*dtheta - dbeta
        alpha = 2*self.theta + self.beta
        wavelength = (np.sin((alpha + dalpha)*np.pi/180) +
                      np.sin((self.beta - dbeta)*np.pi/180)) / \
                     (self.order*self.line_density*1000)

        return Converter.convert_energy_wavelength(wavelength)

    def compute_mirror_corners(self, a, c, v, h, theta, w, l, d):
        theta_g = 90 - theta
        theta_rad = theta_g*np.pi/180

        tlfz = -((a - c * np.tan(theta_rad)) * np.cos(theta_rad)) + h
        tlfy = -(c / np.cos(theta_rad) +
                 (a - c * np.tan(theta_rad)) * np.sin(theta_rad)) + v
        tlfx = -w/2

        trfz = tlfz
        trfy = tlfy
        trfx = w/2

        blfz = tlfz + d*np.sin(theta_rad)
        blfy = tlfy - d*np.cos(theta_rad)
        blfx = -w/2

        brfz = blfz
        brfy = blfy
        brfx = w/2

        tlbz = tlfz - l*np.cos(theta_rad)
        tlby = tlfy - l*np.sin(theta_rad)
        tlbx = -w/2

        trbz = tlbz
        trby = tlby
        trbx = w/2

        blbz = tlbz + d*np.sin(theta_rad)
        blby = tlby - d*np.cos(theta_rad)
        blbx = -w/2

        brbz = blbz
        brby = blby
        brbx = w/2

        self._mirror_plane = Plane(Point3D(tlfx, tlfy, tlfz),
                                   Point3D(trfx, trfy, trfz),
                                   Point3D(tlbx, tlby, tlbz))

        return ((tlfx, tlfy, tlfz),
                (trfx, trfy, trfz),
                (blfx, blfy, blfz),
                (brfx, brfy, brfz),
                (tlbx, tlby, tlbz),
                (trbx, trby, trbz),
                (blbx, blby, blbz),
                (brbx, brby, brbz))

    def compute_grating_corners(self, beta, w, l, d):
        beta_g = 90 + beta
        beta_rad = beta_g*np.pi/180

        blbz = -(l/2)*np.cos(beta_rad)
        blby = -(l/2)*np.sin(beta_rad)
        blbx = -w/2

        brbz = -(l/2)*np.cos(beta_rad)
        brby = -(l/2)*np.sin(beta_rad)
        brbx = w/2

        blfz = (l/2)*np.cos(beta_rad)
        blfy = (l/2)*np.sin(beta_rad)
        blfx = -w/2

        brfz = (l/2)*np.cos(beta_rad)
        brfy = (l/2)*np.sin(beta_rad)
        brfx = w/2

        tlbz = blbz - d*np.sin(beta_rad)
        tlby = blby + d*np.cos(beta_rad)
        tlbx = -w/2

        trbz = brbz - d*np.sin(beta_rad)
        trby = brby + d*np.cos(beta_rad)
        trbx = w/2

        tlfz = blfz - d*np.sin(beta_rad)
        tlfy = blfy + d*np.cos(beta_rad)
        tlfx = -w/2

        trfz = brfz - d*np.sin(beta_rad)
        trfy = brfy + d*np.cos(beta_rad)
        trfx = w/2

        self._grating_plane = Plane(Point3D(blfx, blfy, blfz),
                                    Point3D(brfx, brfy, brfz),
                                    Point3D(blbx, blby, blbz))

        return ((blbz, blby, blbx),
                (brbz, brby, brbx),
                (blfz, blfy, blfx),
                (brfz, brfy, brfx),
                (tlbz, tlby, tlbx),
                (trbz, trby, trbx),
                (tlfz, tlfy, tlfx),
                (trfz, trfy, trfx))

    def propogate(self, ray):
        mirr_args = [self.mirror_hoffset, self.mirror_voffset,
                     self.mirror_axis_voffset, self.mirror_axis_hoffset,
                     self.theta, self.mirror_width,
                     self.mirror_length, self.mirror_height]

        self.compute_mirror_corners(*mirr_args)

        gr_args = [self._grating.beta, self._grating_width,
                   self._grating_length, self._grating_height]

        self.compute_grating_corners(*gr_args)

        mirr_ray, _ = self.bounce(ray, self._mirror_plane)
        # grating_ray, _ = self.bounce(mirr_ray, self._grating_plane)
        grating_ray, _ = self.diffract(mirr_ray, self._grating_plane)

        ray_start_array = [*ray.point]
        mirror_intercept = [*mirr_ray.point]
        grating_intercept = [*grating_ray.point]

        mirror_normal = [[*mirr_ray.point], [*(mirr_ray.point +
                                               self._mirror_plane.normal*50)]]
        grating_normal = [[*grating_ray.point], [*(grating_ray.point +
                                                   self._grating_plane.normal*50)]]

        ray_out = [*(grating_ray.point + grating_ray.vector*5000)]

        points = ([ray_start_array, mirror_intercept,
                   grating_intercept, ray_out],
                  mirror_normal, grating_normal)

        return points

    def bounce(self, ray, plane):
        plane_intersect = plane.intersect(ray)
        ray_array = ray.vector
        mirror_normal = plane.normal
        dp = ray_array.dot(mirror_normal)  # dot product
        refl_vector = (ray_array - 2*dp*mirror_normal).toLength(1)
        refl_ray = Ray3D(plane_intersect, refl_vector)

        return refl_ray, mirror_normal

    def diffract(self, ray, plane):
        dp = ray.vector.dot(plane.normal)
        angle = np.arccos(dp/plane.normal.magnitude/ray.vector.magnitude)
        alpha = (np.pi/2-angle)*180/np.pi
        beta = Grating.compute_beta(90-alpha, self._grating.line_density,
                                    self._grating.energy, self._grating.order)
        diff_ray, _ = self.bounce(ray, plane)
        diff_ray.vector = diff_ray.vector.rotate(-90 - beta - alpha, ['z', 'y'])

        return diff_ray, plane.normal
