from time import time
import numpy as np
import matplotlib.pyplot as plt
from serial import SerialException
from zoidberg import PixhawkNode, episode, change_heading

# Linux address
device = '/dev/ttyACM0'
# Mac OSX address
#device = '/dev/tty.usbmodem1'
# Windows address
#device = 'COM3'

runnum = episode()
pn = PixhawkNode(device)

total_time = 10  # total task time, seconds
target_heading = 80  # random choice

# create dictionary of nodes needed for this task
node_dict = {'pn':pn}

# try loop is used to ensure that communication with pixhawk is
# terminated.
try:
    # startup data stream
    pn.isactive(True)
    pn.change_mode('MANUAL')  # change to manual mode

    is_timeout = change_heading(node_dict, runnum, total_time, target_heading)
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
