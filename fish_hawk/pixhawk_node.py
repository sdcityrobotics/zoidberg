"""
============
Pixhawk node
============
Communication node for pixhawk auto pilot module (APM). The APM requires
communication in two directions, inputs and outputs. The APM receives inputs
of desired motor commands as RC controlls, and outputs various instrument
readings. Currently the APM is responsible for providing heading and depth
information to Zoidberg.

A good deal of this code is taken with small modification from the [ArduSub
GitBook](http://www.ardusub.com/developers/pymavlink.html).
"""
from pymavlink import mavutil
import sys
from time import time, sleep
from utils import timestamp, pause
from pixhawk_readings_t import PixhawkReading
from math import pi

class PixhawkNode:
    """Main communication connection between the pixhawk and Zoidberg"""
    def __init__(self, device):
        """Serial connection specifications
        device is a string specifying serial port location of the pixhawk
        Linux: '/dev/ttyACM0'
        Mac OSX: '/dev/tty.usbmodem1'
        Windows: 'COM7'
        *The numbers at the end of these strings may change*
        """

        self.baud = 11520
        self.device = device
        # currently only know how to request all the possible data
        self.data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
        self.data_rate = 10  # action rate, Hz

        # Define messages of interest from the pixhawk
        self.message_types = ['AHRS2', 'SERVO_OUTPUT_RAW']

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
            if self._mav is None:
                self._mav = mavutil.mavlink_connection(self.device,
                                                       baud=self.baud)
            else:
                self._mav.reset()
            # check that there is a heartbeat
            self._mav.recv_match(type='HEARTBEAT', blocking=True)
            print("Heartbeat from APM (system %u component %u)" %
                (self._mav.target_system, self._mav.target_component))
            print('')

        # comes up when no pixhawk is connected
        if self._mav is None:
            return

        # begin transmitting data
        self._mav.mav.request_data_stream_send(self._mav.target_system,
                                               self._mav.target_component,
                                               self.data_stream_ID,
                                               self.data_rate,
                                               int(bool(to_arm)))

        # Arm/disarm
        self._mav.mav.command_long_send(
            self._mav.target_system,
            self._mav.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            int(bool(to_arm)), 0, 0, 0, 0, 0, 0)

        if to_arm:
            # set mode to stabalize
            self.set_mode('STABILIZE')
        else:
            # close the connection
            self.set_mode('MANUAL')
            self._mav.close()

    def check_readings(self):
        """Update the instrument readings to the latest"""
        if self._mav.port.closed:
            print("Reading from a closed serial port")
            return
        isnew = self._read_buffer()
        # update sensor readings if a reading has changed
        if isnew:
            self.pix_readings.timestamp = timestamp()
            if self._messages['AHRS2'] is not None:
                self.pix_readings.heading = self._messages['AHRS2'].yaw \
                        * 180 / pi
            rc = self._messages['SERVO_OUTPUT_RAW']
            if rc is not None:
                self.pix_readings.rc_out = [rc.servo1_raw, rc.servo2_raw,
                                            rc.servo3_raw, rc.servo4_raw,
                                            rc.servo5_raw, rc.servo6_raw,
                                            rc.servo7_raw, rc.servo8_raw]
            print('heading %.1f'%self.pix_readings.heading)
            print(self.pix_readings.rc_out)

    def change_mode(self, mode):
        """ Change the operation mode of the pixhawk
        mode is a string specifing one of the avalible flight modes
        """
        # Check if mode is available
        if mode not in self._mav.mode_mapping():
            print('Unknown mode : {}'.format(mode))
            print('Try:', list(self._mav.mode_mapping().keys()))
            exit(1)

        # Get mode ID
        mode_id = self._mav.mode_mapping()[mode]
        # Set new mode
        self._mav.mav.set_mode_send(
            self._mav.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id)

        # Check ACK
        ack = False
        ack_msg_id = mavutil.mavlink.MAVLINK_MSG_ID_SET_MODE
        while not ack:
            # Wait for ACK command
            ack_msg = self._mav.recv_match(type='COMMAND_ACK', blocking=True)
            ack_msg = ack_msg.to_dict()

            # Check if command in the same in `set_mode`
            if ack_msg['command'] != ack_msg_id:
                continue

            # Print the ACK result !
            res = mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']]
            print(res.description)
            ack = True

    def send_rc(self, vel_forward=0., vel_side=0., vel_dive=0., vel_turn=0.):
        """Send RC commands to the pixhawk, inputs are between -100 and 100"""
        # check for valid inputs
        if abs(vel_forward) > 100 or abs(vel_side) > 100 \
           or abs(vel_dive) > 100 or abs(vel_turn) > 100:
            print('All command inputs must be between -100 and 100, no command sent')
            return
        # http://mavlink.org/messages/common#MANUAL_CONTROL
        # Warning: Because of some legacy workaround, z will work between [0-1000]
        # where 0 is full reverse, 500 is no output and 1000 is full throttle.
        # x,y and r will be between [-1000 and 1000].
        cmd_forward = vel_forward * 10
        cmd_side = vel_side * 10
        cmd_dive = vel_dive * 5 + 500
        cmd_turn = vel_turn * 10

        self._mav.mav.manual_control_send(self._mav.target_system,
                                          cmd_forward,
                                          cmd_side,
                                          cmd_dive,
                                          cmd_turn,
                                          0)

    def _read_buffer(self):
        """Basic loop, handles incomming comms, outgoing comms, and logging"""
        isnew = False  # assume there won't be any messages
        msg = self._mav.recv_match(type=self.message_types,
                                        blocking=False)
        # log comms untill a None is returned (exhausted buffer)
        while msg is not None:
            isnew = True  # got something
            # save matching message as most recent
            self._messages[msg.name] = msg
            #msg = self._mav.recv_match(type=self.message_types, blocking=False)
            msg = self._mav.recv_match(blocking=False)
        return isnew



if __name__ == "__main__":
    from serial import SerialException
    update_period = 0.05
    # Mac OSX address
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
    except SerialException:
        print('Pixhawk is not connected to %s'%device)
    finally:
        print('Shutting down communication')
        pn.isactive(False)
