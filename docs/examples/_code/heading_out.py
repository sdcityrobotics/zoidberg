from zoidberg import PixhawkNode, pause
from serial import SerialException
from time import time

update_period = 0.05
# Mac OSX address of pixhawk
#device = '/dev/tty.usbmodem1'
device = '/dev/ttyACM0'
pn = PixhawkNode(device)

# try loop is used to ensure that communication with pixhawk is
# terminated.
try:
    # startup data stream
    pn.isactive(True)
    while True:
        loop_start = time()
        pn.check_readings()
        print("Current heading: %.2f"%pn.heading)
        # sleep to maintain constant rate
        pause(loop_start, update_period)
except SerialException:
    print('Pixhawk is not connected to %s'%device)
finally:
    print('Shutting down communication with Pixhawk')
    pn.isactive(False)
