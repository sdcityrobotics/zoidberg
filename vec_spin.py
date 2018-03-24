import numpy as np
import matplotlib.pyplot as plt
import quaternion

C_init = np.quaternion(0, 0, 1, 0)
U_init = np.quaternion(0, 1, 0, 0)

a = np.array([1., 0, 0])
a /= np.linalg.norm(a)

phi = 1  # radians per sec
#P_nb = quaternion.as_quat_array(np.hstack([np.cos(phi / 2),
                                           #np.sin(phi / 2) * a]))
P_nb = quaternion.as_quat_array(np.hstack([0, phi * a]))

dt = 0.05
taxis = np.arange(200) * dt

qdot = np.ones_like(taxis) * P_nb / 2

qs = U_init * np.exp(np.cumsum(qdot) * dt)

C = []
for uq in qs:
    C.append(uq * C_init / uq)

b = quaternion.as_float_array(C)

fig, ax = plt.subplots()
for i, l in enumerate(b.T):
    ax.plot(taxis, l, label='%i'%i)
ax.legend()
ax.grid()
plt.show(block=False)
