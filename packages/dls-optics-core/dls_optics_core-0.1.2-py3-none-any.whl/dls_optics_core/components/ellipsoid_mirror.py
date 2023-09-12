import numpy as np
from optics.components import Mirror


class EllipsoidMirror(Mirror):
    def __init__(self, r1, r2, p, q, theta, rotated=False, **kwargs):
        super(EllipsoidMirror, self).__init__(r1, r2, p, q, p, q,
                                              theta, rotated, **kwargs)

    @property
    def d(self):
        """Half-distance between foci."""
        if self.p_s == np.inf and self.q_s == np.inf:
            return np.inf

        return 0.5*np.sqrt(self.p_t*self.p_t +
                           self.q_t*self.q_t -
                           2*self.p_t*self.q_t*np.cos(2*self.theta*np.pi/180))

    @property
    def a(self):
        """Semi-major axis."""
        return (self.p_t + self.q_t)/2

    @property
    def b(self):
        """Semi-minor axis."""
        return np.sqrt(self.a*self.a - self.d*self.d)

    @property
    def x_m(self):
        """Distance along semi-major axis from centre of
           ellipse to centre of mirror."""
        return (self.p_t*self.p_t - self.q_t*self.q_t) / \
               (2*np.sqrt(self.p_t*self.p_t + self.q_t*self.q_t +
                2*self.p_t*self.q_t*np.cos(2*(90-self.theta)*np.pi/180)))

    @property
    def x_o(self):
        """Distance along major axis from object (source) to mirror centre."""
        return self.x_m + self.d

    @property
    def x_i(self):
        """Distance along major axis from mirror centre to image (sample)."""
        return self.d - self.x_m

    @property
    def eccentricity(self):
        return np.sqrt(1 - self.b*self.b/(self.a*self.a))

    @property
    def roc_t(self):
        """Tangential radius of curvature at mirror centre."""
        return 2*self.p_h*self.q_h/((self.p_h + self.q_h)*np.cos(self.theta*np.pi/180))

    @property
    def roc_s(self):
        j = self.p_h*self.q_h*np.sin(2*(90 - self.theta)*np.pi/180)
        k = np.sqrt(self.p_h*self.p_h + self.q_h*self.q_h +
                    2*self.p_h*self.q_h*np.cos(2*(90-self.theta)*np.pi/180))

        return j/k

    @property
    def l(self):  # noqa: E743
        """Semi-latus rectum (radius of osculating circle at vertex)."""
        return self.get_radius(0)

    @property
    def r_c(self):
        """Radius of osculating circle at centre of mirror."""
        return self.get_radius(self.x_i)

    def get_radius(self, d):
        """Radius of ellipsoid (orthogonal to major axis) at distance d from focus."""
        x = self.d - d

        return (self.b/self.a)*np.sqrt(self.a*self.a - x*x)

    def get_entrance_div(self, d):
        """Divergence from object to point at distance d from image."""
        x = 2*self.d - d
        r = self.get_radius(x)

        return 2*r/self.d_o

    def get_exit_div(self, d):
        """Divergence from image to point at distance d from image."""
        return 2*self.get_radius(d)/d
