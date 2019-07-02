import numpy as np
from time import sleep
import matplotlib.pyplot as plt

from acoustics_node import AcousticsNode

plt.ion()

fc = 30000
an = AcousticsNode(fc)

bout = []
tout = []
arrival_time = None
try:
    an.is_active(True)
    while True:
        if (arrival_time is None and an.arrival_time > 0)\
                or an.arrival_time != arrival_time:
            arrival_time = an.arrival_time
            bout.append(an.bearing)
            tout.append(an.arrival_time)
        sleep(0.001)
finally:
    an.is_active(False)
    # recorded data
    bout = np.array(bout)
    tout = np.array(tout)
    # remove invalid results
    bout = bout[bout > -1000]
    tout = tout[tout > -1000]

fig, ax = plt.subplots()
ax.plot(tout, bout, '.')
