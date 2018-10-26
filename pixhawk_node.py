"""
=================
Read all messages
=================
Since the documenation for pymavlink, mavlink and ardupilot seem to be sparse,
the best way to find an answer to a problem may first be to look at all
possible mesages. This script just prints a ton of messages
"""
from pymavlink import mavutil
import sys
from time import time, sleep
import lcm
from .utils import timestamp, pause
from .pixhawk_readings_t import PixhawkReading

class PixhawkNode:
    """Communication with the pixhawk, and log messages"""
    def __init__(self, device):
        """Setup connection"""
        self.baud = 11520
        self.device = device
        # currently only know how to request all the possible data
        self.data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
        self.data_rate = 10  # action rate, Hz

        # Define messages of interest from the pixhawk
        self.message_types = ['SCALED_IMU2']

        # Define where to save readings
        self.pix_readings = PixhawkReading()

        # internal object to maintain io with pixhawk
        self._mav = None
        # internal dictionary for saving raw messages
        self._messages = dict.fromkeys(self.message_types)

    def isactive(self, to_arm):
        """arm / disarm motors, reset ground control"""
        # start/stop the data stream
        if to_arm:
            self._mav = mavutil.mavlink_connection(self.device, baud=self.baud)
            # check that there is a heartbeat
            self._mav.recv_match(type='HEARTBEAT', blocking=True)
            print("Heartbeat from APM (system %u component %u)" %
                (self._mav.target_system, self._mav.target_component))
            print('')

        self._mav.mav.request_data_stream_send(self._mav.target_system,
                                               self._mav.target_component,
                                               self.data_stream_ID,
                                               self.data_rate,
                                               int(bool(to_arm)))
        if not to_arm:
            self._mav.close()

    def check_readings(self):
        """Update the instrument readings to the latest"""
        if self._mav.port.closed():
            print("Reading from a closed serial port")
            return
        isnew = self._read_buffer()
        # update sensor readings if a reading has changed
        if isnew:
            self.pix_readings.timestamp = timestamp()
            print(self._messages[self.message_types[0]])

    def _read_buffer(self):
        """Basic loop, handles incomming comms, outgoing comms, and logging"""
        isnew = False  # assume there won't be any messages
        msg = mav_connection.recv_match(type=self.message_types,
                                        blocking=False)
        # log comms untill a None is returned (exhausted buffer)
        while msg is not None:
            isnew = True  # got something
            # save matching message as most recent
            self.messages[msg.type] = msg
            msg = mav_connection.recv_match(type=self.message_types,
                                            blocking=False)

if __name__ == "__main__":
    print("hello")
    update_period = 0.05
    # Mac address
    device = '/dev/tty.usbmodem1'
    pn = PixhawkNode(device)

    # try loop is used to ensure that communication with pixhawk is
    # terminated.
    try:
        # startup data stream
        pn.isactive(True)
        while True:
            loop_start = time()
            pn.check_readings()
            # sleep to maintain constant rate
            pause(loop_start, update_period)
    finally:
        pn.isactive(False)
