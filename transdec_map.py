import numpy as np
import matplotlib.pyplot as plt

# Define outer boundry, modeled as two circle arcs
# All units in meters
tip_length = 91.
bridge_length = 61.5
# orgin of coordinate system
bridge_south = np.array([0., 0, 0])
# radius of deep center
center_rad = 50.8 / 2

# setup trignometry of problem
# terms from the internet
sagitta = bridge_length / 2  # r - r cos(theta)
half_cord = tip_length / 2   # r sin(theta)
arc_rad = (sagitta ** 2 + half_cord ** 2) / (2 * sagitta)
dtheta = 2 * np.arcsin(half_cord / arc_rad)

# solve for each arcs center of rotation
arc_south_cor = bridge_south.copy()
arc_south_cor[1] = arc_south_cor[1] + arc_rad

arc_north_cor = bridge_south.copy()
arc_north_cor[1] = arc_north_cor[1] + bridge_length - arc_rad

center_center = bridge_south.copy()
center_center[1] = center_center[1] + bridge_length / 2


# plot the boundaries
num_th = 300
# create a symetric theta boundry
arc_axis = np.arange(num_th) / (num_th - 1) * dtheta - dtheta / 2
center_axis = np.arange(num_th) / (num_th - 1) * np.pi - np.pi / 2

fig, ax = plt.subplots()
ax.plot(arc_south_cor[0] + arc_rad * np.sin(arc_axis),
         arc_south_cor[1] - arc_rad * np.cos(arc_axis), color='C0')

ax.plot(arc_north_cor[0] + arc_rad * np.sin(arc_axis),
        arc_north_cor[1] + arc_rad * np.cos(arc_axis), color='C0')

ax.plot(center_center[0] + center_rad * np.sin(center_axis),
        center_center[1] + center_rad * np.cos(center_axis), color='C1')

ax.plot(center_center[0] + center_rad * np.sin(center_axis),
        center_center[1] - center_rad * np.cos(center_axis), color='C1')

ax.set_title('Plan view of Transdec facility')
ax.set_xlabel('East-West, meters')
ax.set_ylabel('North-South, meters')
ax.set_aspect('equal')
ax.grid()

plt.show(block=False)


