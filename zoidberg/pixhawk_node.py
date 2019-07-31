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
import os
from pymavlink import mavutil
import sys
from time import time, sleep
import numpy as np
from zoidberg import timestamp, empty_value
from math import pi

class PixhawkNode:
    """Main communication connection between the pixhawk and Zoidberg"""
    def __init__(self, port):
        """Serial connection specifications
        port is a string specifying serial port location of the pixhawk
        Linux: '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'
        Mac OSX: '/dev/tty.usbmodem1'
        Windows: 'COM7'
        *Except for Linux, numbers at the end of these strings may change*
        """

        self.baud = 11520
        self.port = port
        # currently only know how to request a lot of data
        self.data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
        #MAV_DATA_STREAM_ALL
        self.data_rate = 10  # action rate, Hz

        # Define messages of interest from the pixhawk
        self.message_types = ['AHRS2', 'SERVO_OUTPUT_RAW', 'SCALED_PRESSURE2']

        # Define where to save readings
        self.timestamp = timestamp()
        self.heading = empty_value
        self.depth = empty_value
        self.rc_command = empty_value * np.ones(4, dtype=np.int_)
        self.rc_out = empty_value * np.ones(8, dtype=np.int_)
        self.mode = ''

        # internal object to maintain io with pixhawk
        self._mav = None
        # internal dictionary for saving raw messages
        self._messages = dict.fromkeys(self.message_types)

    def isactive(self, to_arm):
        """arm / disarm motors, reset ground control"""
        # start/stop the data stream
        if to_arm:
            if self._mav is None:
                self._mav = mavutil.mavlink_connection(self.port,
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
        print('Arm mode set to {}'.format(to_arm))
        self._mav.mav.command_long_send(
            self._mav.target_system,
            self._mav.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            int(bool(to_arm)), 0, 0, 0, 0, 0, 0)

        if to_arm:
            print('Turning compass from 3-D to 2-D readings')
            self._mav.mav.param_set_send(self._mav.target_system,
                                        self._mav.target_component,
                                        b'EK2_MAG_CAL',
                                        2,
                                        mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
            message = self._mav.recv_match(type='PARAM_VALUE', blocking=True).to_dict()
            print('name: %s\tvalue: %d' % (message['param_id'], message['param_value']))
            # set mode to stabalize
            self.change_mode('MANUAL')
        else:
            # close the connection
            self.change_mode('MANUAL')
            self._mav.close()
        print()

    def check_readings(self):
        """Update the instrument readings to the latest"""
        if self._mav.port.closed:
            print("Reading from a closed serial port")
            return
        isnew = self._read_buffer()
        # update sensor readings if a reading has changed
        if isnew:
            self.timestamp = timestamp()
            if self._messages['AHRS2'] is not None:
                # convert from radians to degrees
                yaw_deg = self._messages['AHRS2'].yaw * 180 / pi
                # convert from (-180, 180) range to (0, 360) range
                if yaw_deg < 0:
                    yaw_deg += 360
                self.heading = yaw_deg
            rc = self._messages['SERVO_OUTPUT_RAW']
            if rc is not None:
                self.rc_out = [rc.servo1_raw, rc.servo2_raw, rc.servo3_raw,
                               rc.servo4_raw, rc.servo5_raw, rc.servo6_raw,
                               rc.servo7_raw, rc.servo8_raw]
                self.rc_out = np.array(self.rc_out)
            sp_msg = self._messages['SCALED_PRESSURE2']
            if sp_msg is not None:
                # converte from hPa to dBar
                self.depth = sp_msg.press_diff * .01

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
            print('Changing mode to '+ mode)
            res = mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']]
            print(res.description)
            print()
            ack = True

    def send_rc(self, vel_forward=0., vel_side=0., vel_dive=0., vel_turn=0.):
        """Send RC commands to the pixhawk, inputs are between -100 and 100"""
        # check for valid inputs
        if abs(vel_forward) > 100 or abs(vel_side) > 100 \
           or abs(vel_dive) > 100 or abs(vel_turn) > 100:
            print('All command inputs must be between -100 and 100, no command sent')
            return
        # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
        cmd_forward = int(vel_forward * 5 + 1500)
        cmd_side = int(vel_side * 5 + 1500)
        cmd_dive = int(vel_dive * 5 + 1500)
        cmd_turn = int(vel_turn * 5 + 1500)

        # record most recent command
        self.rc_command = np.array([vel_forward, vel_side, vel_dive, vel_turn],
                                   dtype=np.int_)
        rc_out = [65535] * 8
        # channel mapping from
        # http://www.ardusub.com/operators-manual/rc-input-and-output.html#rc-inputs
        rc_out[2] = cmd_dive
        rc_out[3] = cmd_turn
        rc_out[4] = cmd_forward
        rc_out[5] = cmd_side

        self._mav.mav.rc_channels_override_send(self._mav.target_system,
                                                self._mav.target_component,
                                                *rc_out)

    def log(self, episode_name):
        """Save current state to a log file"""
        if not os.path.isdir(episode_name):
            os.makedirs(episode_name)
        save_name = os.path.join(episode_name, 'mission_log.txt')
        state = self.timestamp + ', {:.03f}, {:.03f}'.format(
                  self.heading, self.depth)
        state += ', ' + np.array_str(self.rc_out) + '\n'

        with open(save_name, 'a') as f:
            f.write(state)

    def _read_buffer(self):
        """Basic loop, handles incomming comms, outgoing comms, and logging"""
        isnew = False  # assume there won't be any messages
        msg = self._mav.recv_match(type=self.message_types,
                                        blocking=False)
        # log comms untill a None is returned (exhausted buffer)
        while msg is not None:
            isnew = True  # got something
            # save matching message as most recent
            if msg.get_msgId() != -1:
                if msg.name in self.message_types:
                    self._messages[msg.name] = msg
            #msg = self._mav.recv_match(type=self.message_types, blocking=False)
            msg = self._mav.recv_match(blocking=False)
        return isnew
