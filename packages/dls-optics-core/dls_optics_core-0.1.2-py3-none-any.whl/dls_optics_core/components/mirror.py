import numpy as np
from optics.components import Element
from optics.beam import Beam, Image


class Mirror(Element):
    def __init__(self, r1, r2, p_h, q_h, p_v, q_v, theta, rotated=False, **kwargs):
        super(Mirror, self).__init__(r1, r2, theta, rotated, **kwargs)

        self.p_h = p_h
        self.q_h = q_h
        self.p_v = p_v
        self.q_v = q_v

    @property
    def r_s(self):
        """Sagittal radius."""
        if self.p_s == np.inf and self.q_s == np.inf:
            return np.inf

        return 2*np.cos(self.theta*np.pi/180)/(1/self.p_s + 1/self.q_s)

    @r_s.setter
    def r_s(self, r_s):
        pass

    @property
    def r_t(self):
        """Tangential radius."""
        if self.p_t == np.inf and self.q_t == np.inf:
            return np.inf

        return 2/np.cos(self.theta*np.pi/180)/(1/self.p_t + 1/self.q_t)

    @r_t.setter
    def r_t(self, r_t):
        pass

    @property
    def f_t(self):
        return 1/(1/self.p_t + 1/self.q_t)

    @property
    def f_s(self):
        return 1/(1/self.p_s + 1/self.q_s)

    @property
    def f_h(self):
        return self.f_t if self.rotated else self.f_s

    @property
    def f_v(self):
        return self.f_s if self.rotated else self.f_t

    def propogate(self, beam):
        """Get beam transmitted by mirror."""
        input_image = beam.propogate(self.r1)
        transformed_image = self.transform(input_image)
        exit_beam = Beam(transformed_image)

        return exit_beam.propogate(self.r2)

    def transform(self, image):
        w = image.width
        h = image.height
        h_div = -image.h_div*self.p_h/self.q_h
        v_div = -image.v_div*self.p_v/self.q_v

        return Image(w, h, h_div, v_div)

    def offset_angle(self, offset):
        theta_new = self.theta + offset

        if self.r_t == np.inf:
            q_t_new = np.inf
        else:
            a = self.r_t*np.cos(theta_new*np.pi/180)/2 - 1/self.p_t
            q_t_new = 1/a

        if self.r_s == np.inf:
            q_s_new = np.inf
        else:
            b = 2*np.cos(theta_new*np.pi/180)/self.r_s - 1/self.p_s
            q_s_new = 1/b

        return (q_t_new, q_s_new)
