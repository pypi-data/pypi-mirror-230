import numpy as np


class Element(object):
    def __init__(self, r1=0, r2=0, theta=0, rotated=False, **kwargs):
        super().__init__(**kwargs)
        self.r1 = r1
        self.r2 = r2
        self.theta = theta
        self.rotated = rotated

        self.p_h = np.inf
        self.q_h = np.inf
        self.p_v = np.inf
        self.q_v = np.inf

    @property
    def p_t(self):
        return self.p_h if self.rotated else self.p_v

    @property
    def p_s(self):
        return self.p_v if self.rotated else self.p_h

    @property
    def q_t(self):
        return self.q_h if self.rotated else self.q_v

    @property
    def q_s(self):
        return self.q_v if self.rotated else self.q_h

    @property
    def demagnification_h(self):
        return self.p_h/self.q_h

    @property
    def demagnification_v(self):
        return self.p_v/self.q_v

    def footprint(self, beam):
        """Beam footprint on the element (tangential, sagittal)."""
        beam.propogate(self.r1)

        w = beam.final_width
        h = beam.final_height

        t = w/np.cos(self.theta*np.pi/180) if self.rotated else h/np.cos(self.theta*np.pi/180)
        s = h if self.rotated else w

        return t, s

    def image_at_element(self, beam):
        return beam.propogate(self.r1)

    def propogate(self, beam):
        return beam.propogate(self.r1 + self.r2)
