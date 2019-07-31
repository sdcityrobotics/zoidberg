"""
Tank test

Run 3 basic motion behviors in a row.
"""

from time import time
import numpy as np
import matplotlib.pyplot as plt
from serial import SerialException
from zoidberg import PixhawkNode, episode, change_heading,\
                     change_depth, drive_robot

# Linux address
device = '/dev/ttyACM0'
# Mac OSX address
#device = '/dev/tty.usbmodem1'
# Windows address
#device = 'COM3'

target_heading = 80  # random choice - will be changed after calibrating in pool
target_depth = 0.3  # not too deep for a tank test
forward_speed = 10  # not too fast for a tank test
side_speed = 10 # not too fast of a value

heading_time = 10  # max heading task time, seconds
depth_time = 10  # max depth task time, seconds
drive_time = 10  # max drive task time, seconds
total_time = 10

# setup devices
pn = PixhawkNode(device)

# uncomment to test the zed camera
# zn = ZedNode(device)

# create dictionary of nodes needed for this task
node_dict = {'pn':pn}

# uncomment to test the zed camera
# node_dict = {'pn':pn, 'zn':zn}

runnum = episode()
# try loop is used to ensure that communication with pixhawk is
# terminated.
try:
    # startup data stream
    pn.isactive(True)

    is_timeout = change_heading(node_dict, runnum, total_time, target_heading)
    is_timeout = change_depth(node_dict, runnum, total_time, target_depth)
    is_timeout = drive_robot(node_dict, runnum, total_time, speed_forward=forward_speed, speed_side=side_speed)

    if is_timeout:
        print('Reached desired heading')
    else:
        print('Mission timed out')

except SerialException:
    print('Pixhawk is not connected to %s'%device)
    raise
finally:
    print('Shutting down communication')
    pn.isactive(False)
