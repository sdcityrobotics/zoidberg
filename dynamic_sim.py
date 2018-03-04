"""
=================================
Rigid body simulator of submarine
=================================
Submarine is modeled as a solid cylinder with 4 motors in a quad copter configuration.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PatchCollection

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

theta_dot = lambda td_last, fvec: td_last + theta_ddot(F1, F2, F3, F4) * dt

theta = lambda t_last, td_last, fvec: t_last + theta_dot(td_last, F1, F2, F3, F4) * dt

# attitude vector is defined (yaw, pitch, roll)
attitude = np.array([0., 0, 0])

rec_top = [mpatches.Rectangle([-fh_rad / 2, -fh_length / 2], fh_rad, fh_length)]
col_top = PatchCollection(rec_top)

th_axis = np.arange(300) / 300 * 2 * np.pi
l_axis = np.arange(301) / 300 * fh_length
r_axis = np.ones_like(l_axis) * fh_rad

def get_rot(att_vec):
    """rotate object to desired attitude
    formulation is from 'General rotations' section of wikipedia article
    order of matrix multiplication is important
    """
    att_vec = np.array(att_vec)

    Rz = np.array([[np.cos(att_vec[0]), -np.sin(att_vec[0]), 0],
                   [np.sin(att_vec[0]), np.cos(att_vec[0]), 0],
                   [0, 0, 1]])

    Ry = np.array([[np.cos(att_vec[1]), 0, np.sin(att_vec[1])],
                   [0, 1, 0],
                   [-np.sin(att_vec[1]), 0, np.cos(att_vec[1])]])

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(att_vec[2]), -np.sin(att_vec[2])],
                   [0, np.sin(att_vec[2]), np.cos(att_vec[2])]])

    X = np.cos(th_axis)[:, None] * r_axis
    Y = np.ones_like(th_axis)[:, None] * l_axis
    Z = np.sin(th_axis)[:, None] * r_axis

    rot = np.array([X, Y, Z])
    rot = np.moveaxis(rot, 0, 1)
    rot = Rx @ rot
    rot = Ry @ rot
    rot = Rz @ rot
    rot = np.moveaxis(rot, 1, 0)
    return rot[0, :, :], rot[1, :, :], rot[2, :, :]

X, Y, Z = get_rot([0.2, 0, 0])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z)
ax.set_xlim(-fh_length, fh_length)
ax.set_ylim(-fh_length, fh_length)
ax.set_zlim(-fh_length, fh_length)


plt.show(block=False)
