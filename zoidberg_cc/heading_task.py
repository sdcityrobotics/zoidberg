from time import time
import numpy as np
import matplotlib.pyplot as plt
from serial import SerialException
from zoidberg import PixhawkNode, pause, episode, actionperiod, main_loop, \
                     constant_r_task, constant_r_success

# Linux address
device = '/dev/ttyACM0'
# Mac OSX address
#device = '/dev/tty.usbmodem1'
# Windows address
#device = 'COM3'

runnum = episode()
pn = PixhawkNode(device)

total_time = 30  # total task time, seconds
target_heading = 80  # random choice
r_P = 3  # proportionality constant for heading correction
r_max = 70  # max rate of turn
r_tol = 2  # if we are within this number of degrees, we have succeeded

# create dictionary of nodes needed for this task
node_dict = {'pn':pn}

# try loop is used to ensure that communication with pixhawk is
# terminated.
try:
    # startup data stream
    pn.isactive(True)
    pn.change_mode('MANUAL')  # change to manual mode

    r_task = constant_r_task(target_heading, r_P, r_max)
    r_succ = constant_r_success(target_heading, r_tol)

    main_loop(node_dict, runnum, total_time, isdone=r_succ, get_r=r_task)
    print('Reached desired heading')

except SerialException:
    print('Pixhawk is not connected to %s'%device)
    raise
finally:
    print('Shutting down communication')
    pn.isactive(False)
