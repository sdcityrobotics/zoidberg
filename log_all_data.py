"""
=======================================
Read all messages and write to log file
=======================================
It is important to log all received infromation, luckily this is pretty simple
with pymavlink. In the future MAVROS will provide this saving capability.
"""

import numpy as np
import matplotlib.pyplot as plt
from pymavlink import mavutil
import sys
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
log_file = 'all_out.log'
device = '/dev/tty.usbmodem1'

# currently only know how to request all the possible data
data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
#data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS
#data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_RAW_CONTROLLER
#data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_RAW_SENSORS
data_rate = 100

# number of messages to read
num_points = 100

def read_messages(mav_obj, file_obj):
    """
    Read accelerometer readings until taxis is exhausted.
    There will only be output once the total time has elapsed.
    """
    msg = mav_obj.recv_match(blocking=True)
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            # flush out all bad data msgs at start
            sys.stdout.write(msg.data)
            sys.stdout.flush()
    i = 0
    while i < num_points:
        msg = mav_obj.recv_match(blocking=True)
        # don't bother saving heartbeats
        if msg.get_type() == 'HEARTBEAT':
            continue
        # if something catches your interest, pull out that msg type
        #msg = mav_obj.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        file_obj.write(str(msg))
        file_obj.write('\n')
        i += 1

mav = mavutil.mavlink_connection(device, baud=11520)
# a try block ensures that mav with always be closed

try:
    # check that there is a heartbeat
    mav.recv_match(type='HEARTBEAT', blocking=True)
    print("Heartbeat from APM (system %u component %u)" %
        (mav.target_system, mav.target_component))
    print('')
    mav.mav.request_data_stream_send(mav.target_system,
                                     mav.target_component,
                                     data_stream_ID,
                                     data_rate,
                                     1)
    with open(log_file, 'w+') as f:
        read_messages(mav, f)
finally:
    # close the connection
    mav.mav.request_data_stream_send(mav.target_system,
                                     mav.target_component,
                                     data_stream_ID,
                                     data_rate,
                                     0)
    mav.close()
