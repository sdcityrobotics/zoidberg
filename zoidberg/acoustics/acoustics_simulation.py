import numpy as np
from time import sleep
import matplotlib.pyplot as plt

from acoustics_node import AcousticsNode

plt.ion()

fc = 30000
an = AcousticsNode(fc)

bout = []
tout = []
ampsout = []
timestamp = None
try:
    an.is_active(True)
    while True:
        if (timestamp is None and an.timestamp is not None)\
                or an.timestamp != timestamp:
            timestamp = an.timestamp
            bout.append(an.bearing)
            tout.append(an.arrival_time)

            if an.recorded_data is not None:
                ampsout.append(np.abs(an.recorded_data[0, :]))
        sleep(0.01)
finally:
    an.is_active(False)
    # recorded data
    bout = np.array(bout)
    tout = np.array(tout)
    ampsout = np.concatenate(ampsout)
    # remove invalid results
    bout = bout[bout > -1000]
    tout = tout[tout > -1000]



