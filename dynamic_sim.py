"""
=================================
Rigid body simulator of submarine
=================================
Submarine is modeled as a solid cylinder with 4 motors in a quad copter configuration.
"""

import numpy as np
import matplotlib.pyplot as plt

fh_length = 1.5  # m
fh_rad = 0.15  # m
fh_mass = 8.  # kg

I_x = 1. / 2 * fh_mass * fh_rad ** 2
I_y = 1. / 12 * fh_mass * (3 * fh_rad ** 2 + fh_length ** 2)
I_z = 1. / 12 * fh_mass * (3 * fh_rad ** 2 + fh_length ** 2)
I_invt = np.diag([1 / I_x, 1 / I_y, 1 / I_z])

# motor offset from COG vector
rvec = fh_length * np.array([[-0.5, 0.5, -0.5],
                             [0.5, 0.5, -0.5],
                             [0.5, -0.5, -0.5],
                             [-0.5, -0.5, -0.5]])

# motor attitude vector
mvec = np.array([[0., 0, 1],
                 [0., 0, 1],
                 [0., 0, 1],
                 [0., 0, 1]])

# acceleration is defined in body relative coordinate frame
x_ddot = lambda fvec: np.sum(fvec[:, None] * mvec, axis=0) / fh_mass

# angulat acceleration is defined in body relative coordinate frame
theta_ddot = lambda fvec: np.dot(I_invt, (F1 * np.cross(r1, m1)
                                                    + F2 * np.cross(r2, m2)
                                                    + F3 * np.cross(r3, m3)
                                                    + F4 * np.cross(r4, m4)))

theta_dot = lambda td_last, fvec: td_last \
                                            + theta_ddot(F1, F2, F3, F4) * dt

theta = lambda t_last, td_last, fvec: t_last\
                                                + theta_dot(td_last, F1, F2, F3, F4) * dt
