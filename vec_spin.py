import numpy as np
import matplotlib.pyplot as plt
import quaternion

C_init = np.quaternion(0, 0, 0, 1)  # z-up vector
U_init = np.quaternion(1, 0, 0, 0)

a = np.array([1., 0, 0])
a /= np.linalg.norm(a)

phi = 1  # radians per sec
#P_nb = quaternion.as_quat_array(np.hstack([np.cos(phi / 2),
                                           #np.sin(phi / 2) * a]))
P_nb = quaternion.as_quat_array(np.hstack([0, phi * a]))

dt = 0.05
taxis = np.arange(200) * dt
U = [U_init]

for t in taxis[1:]:
    U.append(U[-1] + U[-1] * P_nb / 2 * dt)

C = []
for uq in U:
    C.append(uq * C_init / uq)

b = quaternion.as_float_array(C)

fig, ax = plt.subplots()
for i, l in enumerate(b.T):
    ax.plot(taxis, l, label='%i'%i)
ax.legend()
ax.grid()
plt.show(block=False)
