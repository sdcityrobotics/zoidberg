from time import time
import numpy as np
import matplotlib.pyplot as plt
from serial import SerialException
from zoidberg import PixhawkNode, pause, episode

update_period = 0.05
# Mac OSX address
device = '/dev/tty.usbmodem1'
# Linux address
#device = '/dev/ttyACM0'
# Windows address
#device = 'COM3'

runnum = episode()
pn = PixhawkNode(device)
pn.isactive(True)
# try loop is used to ensure that communication with pixhawk is
# terminated.

try:
    # startup data stream
    pn.isactive(True)
    # change mode
    pn.change_mode('MANUAL')
    motor_out = []
    readtime = []

    total_time = 3  # total collection time, seconds
    run_start = time()
    loop_start = run_start

    while run_start + total_time > loop_start:
        loop_start = time()
        pn.check_readings()
        pn.send_rc(vel_dive=80)
        pn.log(runnum)
        # sleep to maintain constant rate
        pause(loop_start, update_period)

except SerialException:
    print('Pixhawk is not connected to %s'%device)
    raise
finally:
    print('Shutting down communication')
    pn.isactive(False)


