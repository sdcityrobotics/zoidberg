"""
=================================
Rigid body simulator of submarine
=================================
Submarine is modeled as a solid cylinder with 4 motors in a quad copter configuration.
"""

import numpy as np
import quaternion
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PatchCollection

fh_length = 1.5  # m
fh_rad = 0.3  # m
mot_l = .4
mot_w = .1
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

# sub model
# main body tube
th_axis = np.arange(300) / 300 * 2 * np.pi
l_axis = np.arange(301) / 300 * fh_length - fh_length / 2
r_axis = np.ones_like(l_axis) * fh_rad
# may as well add end caps
cap_len = 60
r_axis[:cap_len] *= np.sin(np.pi * (l_axis[:cap_len] - l_axis[0])
                           / (2 * (l_axis[cap_len] - l_axis[0])))
r_axis[-cap_len:] *= np.sin(np.pi / 2 +
                            np.pi * (l_axis[-cap_len:] - l_axis[-cap_len])
                            / (2 * (l_axis[-1] - l_axis[-cap_len])))

tube_pos = np.array([np.ones_like(th_axis)[:, None] * l_axis,
                     np.cos(th_axis)[:, None] * r_axis,
                     np.sin(th_axis)[:, None] * r_axis])
tube_pos = np.moveaxis(tube_pos, 0, -1)

# motors
l_axis = np.arange(301) / 300 * mot_l
r_axis = np.ones_like(l_axis) * mot_w
r_axis[:cap_len] *= np.sin(np.pi * (l_axis[:cap_len] - l_axis[0])
                           / (2 * (l_axis[cap_len] - l_axis[0])))
r_axis[-cap_len:] *= np.sin(np.pi / 2 +
                            np.pi * (l_axis[-cap_len:] - l_axis[-cap_len])
                            / (2 * (l_axis[-1] - l_axis[-cap_len])))

mot_pos = np.array([np.ones_like(th_axis)[:, None] * l_axis,
                    np.cos(th_axis)[:, None] * r_axis,
                    np.sin(th_axis)[:, None] * r_axis])
mot_pos = np.moveaxis(mot_pos, 0, -1)

xpos = []
for r, m in zip(rvec, mvec):
    # cylinder is defined in [1, 0, 0] direction, rotate to motor attitude
    qf = np.quaternion(0, 1, 0, 0) / np.quaternion(*m)
    qf = qf.sqrt()
    qx = np.concatenate((np.zeros(list(mot_pos.shape[:2]) + [1]),
                         mot_pos), axis=-1)
    qx = quaternion.as_quat_array(qx)
    xpos.append(quaternion.as_float_array(qf * qx / qf)[:, :, 1:] + r)

sub_model = np.concatenate(xpos + [tube_pos])

def get_rot(att_vec):
    """rotate object to desired attitude
    formulation is from 'General rotations' section of wikipedia article
    order of matrix multiplication is important
    """
    att_vec = np.array(att_vec)
    return sub_model[:, :, 0], sub_model[:, :, 1], sub_model[:, :, 2]

X, Y, Z = get_rot([0.2, 0, 0])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(X, Y, Z)
ax.set_xlim(-fh_length, fh_length)
ax.set_ylim(-fh_length, fh_length)
ax.set_zlim(-fh_length, fh_length)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')


plt.show(block=False)
