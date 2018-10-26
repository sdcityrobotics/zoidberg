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
import zoidberg_lcm

class PixhawkNode:
    """Communication with the pixhawk, and log messages"""
    def __init__(self, device):
        """Setup connection"""
        self.baud = 11520
        self.device = device
        # currently only know how to request all the possible data
        self.data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
        self.data_rate = 10  # action rate, Hz

        # prepare a log file
        self.log_file = 'pix_log.txt'
        self.message_types = ['SCALED_IMU2']

        # initilize lcm connection
        self.lc = lcm.LCM()
        self.lcm_channel = 'navigation'

    def start(self):
        """infinite loop, communication and logging"""
        # try loop is used to ensure that communication with pixhawk is
        # terminated.
        mav = mavutil.mavlink_connection(self.device, baud=self.baud)

        # check that there is a heartbeat
        mav.recv_match(type='HEARTBEAT', blocking=True)
        print("Heartbeat from APM (system %u component %u)" %
            (mav.target_system, mav.target_component))
        print('')

        try:

            # startup data stream
            self._ready_vessel(mav, True)

            update_period = 1 / self.data_rate  # seconds

            while True:
                loop_start = time()
                self._read_buffer(mav)
                self._publish_pixhawk_readings(mav)
                self._get_commands()
                self._write_commands(mav)

                # sleep to maintain constant rate
                tsleep = loop_start + update_period - time()
                if tsleep > 0:
                    sleep(tsleep)

        finally:
            self._ready_vessel(mav, False)
            mav.close()

    def _ready_vessel(self, mav_connection, to_arm):
        """arm / disarm motors, reset ground control"""
        # start/stop the data stream
        mav.mav.request_data_stream_send(mav.target_system,
                                        mav.target_component,
                                        self.data_stream_ID,
                                        self.data_rate,
                                        int(bool(to_arm)))

    def _read_buffer(self, mav_connection):
        """Basic loop, handles incomming comms, outgoing comms, and logging"""
        msg = mav_connection.recv_match(type=self.message_types,
                                        blocking=False)
        # log comms untill a None is returned (exhausted buffer)
        while msg is not None:
            # save matching message as most recent
            self.messages[msg.type] = msg
            msg = mav_connection.recv_match(type=self.message_types,
                                            blocking=False)

    def _publish_pixhawk_readings(self):
        """Publish most recent published messages from the Pixhawk"""
        msg = zoidberg_lcm.pixhawk_readings_t()
        # create a timestamp from midnight in milliseconds
        msg.timestamp = int(time() * 1000)
        self.lc.publish(self.lcm_channel, msg.encode())

    def _get_commands(self, mav_connection):
        """Get the most recent mission output for the pixhawk"""
        pass

    def _write_commands(self, mav_connection):
        """Write most recent commands to pixhawk"""
        pass

if __name__ == "__main__":
    print("hello")
    # Mac address
    device = '/dev/tty.usbmodem1'
    pn = PixhawkNode(device)
    pn.start()
