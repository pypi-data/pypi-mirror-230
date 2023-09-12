import numpy as np
from optics.components import Mirror


class ParaboloidMirror(Mirror):
    def __init__(self, r1, r2, q, theta, rotated=False, **kwargs):
        super(ParaboloidMirror, self).__init__(r1, r2, np.inf, q, np.inf, q,
                                               theta, rotated, **kwargs)

    @property
    def f(self):
        return self.q_t*np.power(np.cos(self.theta*np.pi/180), 2)

    @property
    def y0(self):
        return 2*self.f*np.tan(self.theta*np.pi/180)

    @property
    def x0(self):
        return self.f*np.power(np.tan(self.theta*np.pi/180), 2)

    @property
    def parabola_p(self):
        return 2*self.f

    def get_radius(self, d):
        """Radius of paraboloid (orthogonal to parent parabola optical axis)
        at distance d from focus"""
        x = d - self.f

        return np.sqrt(4*self.f*x)

    def get_slope(self, d):
        y = self.get_radius(d)
        return 2*self.f/y
