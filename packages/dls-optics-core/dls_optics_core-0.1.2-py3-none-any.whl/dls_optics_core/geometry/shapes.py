import numpy as np


class Ellipse:
    def __init__(self, p, q, theta):
        self.f = 0.5*np.sqrt(p*p + q*q - 2*p*q*np.cos(2*theta*np.pi/180))
        self.a = (p + q)/2
        self.b = np.sqrt(self.a*self.a - self.f*self.f)
        self.x_m = (p*p - q*q) / (2*np.sqrt(p*p + q*q + 2*p*q*np.cos(2*(90-theta)*np.pi/180)))
        self.p = p
        self.q = q
        self.theta = theta
        self.alpha = np.arctan(self.b*self.b*self.x_m/(self.get_y(self.x_m)*self.a*self.a))
        self.y_0 = self.get_y(self.x_m)

    def __str__(self):
        return "Ellipse:\n" + "a: {:.2f}\n".format(self.a) + \
            "b: {:.2f}\n".format(self.b) + \
            "x_m: {:.2f}\n".format(self.x_m) + \
            "alpha: {:.2f}\n".format(self.alpha)

    def get_y(self, x):
        return (self.b/self.a)*np.sqrt(self.a*self.a - x*x)

    def get_sag(self, x):
        d = self.x_m + x
        y = self.y_0 - self.get_y(d)

        x_prime = x*np.cos(-self.alpha) - y*np.sin(-self.alpha)
        y_prime = x*np.sin(-self.alpha) + y*np.cos(-self.alpha)

        return x_prime, y_prime

    def get_curvature(self, x):
        y = self.get_y(x)
        return (1/np.power(self.a*self.b, 2))*np.power(x*x/np.power(self.a, 4) + \
                                                       y*y/np.power(self.b, 4), -3/2)


class Cylinder:
    def __init__(self, p=1, q=1, theta=89, sagittal=False, r=None):
        if not r is None:
            self.r = r
        elif sagittal:
            self.r = 2*np.cos(theta*np.pi/180)*(1/(1/p + 1/q))
        else:
            self.r = (2/np.cos(theta*np.pi/180))*(1/(1/p + 1/q))

        self.p = p
        self.q =q
        self.theta = theta

    def get_sag(self, x):
        return self.r - np.sqrt(self.r*self.r - x*x)


class Torus:
    def __init__(self, p_t=1, q_t=1, p_s=1, q_s=1, theta=89, r_t=None, r_s=None):
        if not r_t is None:
            self.cylinder_t = Cylinder(r=r_t)
        else:
            self.cylinder_t = Cylinder(p_t, q_t, theta)

        if not r_s is None:
            self.cylinder_s = Cylinder(r=r_s)
        else:
            self.cylinder_s = Cylinder(p_s, q_s, theta, sagittal=True)

        self.r_t = self.cylinder_t.r
        self.r_s = self.cylinder_s.r
        self.p_t = p_t
        self.q_t = q_t
        self.p_s = p_s
        self.q_s = q_s
        self.theta = theta

    def get_sag(self, x, y):
        sagittal_sag = self.cylinder_s.get_sag(y)
        rt_prime = self.r_t - sagittal_sag
        sts_prime = np.sqrt(rt_prime*rt_prime - x*x)

        return self.r_t - sts_prime


class EllipticTorus:
    def __init__(self, p_t, q_t, p_s, q_s, theta):
        self.ellipse = Ellipse(p_t, q_t, theta)
        self.a = self.ellipse.a
        self.b = self.ellipse.b
        self.f = self.ellipse.f
        self.x_m = self.ellipse.x_m

        self.cylinder = Cylinder(p_s, q_s, theta, sagittal=True)
        self.r_s = self.cylinder.r

    def get_sag(self, x, y, correct_alpha=True):
        x_prime = x + self.x_m
        s = self.ellipse.get_y(x_prime)
        s_0 = self.ellipse.get_y(self.x_m)
        r = 1/self.ellipse.get_curvature(x_prime)

        # angle of ellipse tangent w.r.t. x-axis
        alpha = np.arctan(self.b*self.b*x_prime/(s*self.a*self.a))
        alpha_0 = np.arctan(self.b*self.b*self.x_m/(s_0*self.a*self.a))

        # coordinates of local radius centre in global ellipse coordinates
        x_c = x_prime - r*np.sin(alpha)
        z_c = r*np.cos(alpha) - s

        sagittal_sag = self.cylinder.get_sag(y)
        rt_prime = r - sagittal_sag

        z = z_c - np.sqrt(rt_prime*rt_prime - np.power(x_prime - x_c, 2)) + s_0

        if correct_alpha:
            et_x = x*np.cos(-alpha_0) - z*np.sin(-alpha_0)
            et_z = x*np.sin(-alpha_0) + z*np.cos(-alpha_0)
        else:
            et_x = x
            et_z = z

        return et_z, et_x
