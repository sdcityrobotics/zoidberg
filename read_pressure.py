"""
======================
Read pressure data
======================
Simple demonstration of how to read from the pyhawk. First a communication
link is established, then a request is sent for it to start sending out
imformation. Then it is simply a matter of finding the information of interest,
and saving the output.
"""

import numpy as np
import matplotlib.pyplot as plt
from pymavlink import mavutil
import glob

# The first challenge is to find the pyxhawk device name. On linux:
#device = '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'
# This may require that you add yourself to the user group dialout
# If you get a permission denied error, see
# https://unix.stackexchange.com/questions/14354/read-write-to-a-serial-port-without-root#14363

# Mac recipe
# before inserting the pyxhawk into the computer
# Be sure to comment out lines till device.pop() once device is defined
# b4 = glob.glob('/dev/tty*')
## after inserting the pyxhawk into the computer
#a4 = glob.glob('/dev/tty*')
## find the set difference between the two glob lists. this is the pyxhawk
#device = set(a4).difference(set(b4))
#device = device.pop()
device = '/dev/tty.usbmodem1'

# currently only know how to request all the possible data
data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
data_rate = 10

# plot the output
num_points = 100
taxis = np.arange(num_points, dtype=np.float_) / num_points * data_rate


def read_accelerometer(mav_obj, taxis):
    """
    Read accelerometer readings until taxis is exhausted.
    There will only be output once the total time has elapsed.
    """
    msg_type = 'SCALED_PRESSURE2'
    press = []

    msg = mav_obj.recv_match(blocking=True)
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
    elif msg.get_type() == msg_type:
        press.append(msg.press_abs)

    for t in taxis:
        msg = mav_obj.recv_match(type=msg_type, blocking=True)
        press.append(msg.press_abs)
    return press

mav = mavutil.mavlink_connection(device, baud=11520)
# check that there is a heartbeat
mav.recv_match(type='HEARTBEAT', blocking=True)
print("Heartbeat from APM (system %u component %u)" %
      (mav.target_system, mav.target_component))
print('')


# a try block ensures that mav with always be closed
try:
    # open the connection
    mav.mav.request_data_stream_send(mav.target_system,
                                     mav.target_component,
                                     data_stream_ID,
                                     data_rate,
                                     1)

    print('Recording pressure for %.1f seconds'%np.max(taxis))
    press = read_accelerometer(mav, taxis)
finally:
    # close the connection
    mav.mav.request_data_stream_send(mav.target_system,
                                     mav.target_component,
                                     data_stream_ID,
                                     data_rate,
                                     0)
    mav.close()

fig, ax = plt.subplots()

ax.set_title('Recorded pressure data')
ax.plot(taxis, press)
ax.grid()
ax.set_ylabel('pressure, hectopascal')
ax.set_xlabel('time, sec')

plt.show()
