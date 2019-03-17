"""
=================
Read all messages
=================
Since the documenation for pymavlink, mavlink and ardupilot seem to be sparse,
the best way to find an answer to a problem may first be to look at all
possible mesages. This script just prints a ton of messages
"""
from pymavlink import mavutil
# The first challenge is to find the pyxhawk device name. On linux:
#device = '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'
# This may require that you add yourself to the user group dialout
# If you get a permission denied error, see
# https://unix.stackexchange.com/questions/14354/read-write-to-a-serial-port-without-root#14363

# Mac and PC recipe
# before inserting the pyxhawk into the computer
# Be sure to comment out lines till device.pop() once device is defined
# b4 = glob.glob('/dev/tty*')
## after inserting the pyxhawk into the computer
#a4 = glob.glob('/dev/tty*')
## find the set difference between the two glob lists. this is the pyxhawk
#device = set(a4).difference(set(b4))
#device = device.pop()

# Mac address
device = '/dev/tty.usbmodem1'
#device = '/dev/ttyACM0'

# currently only know how to request all the possible data
data_stream_ID = mavutil.mavlink.MAV_DATA_STREAM_ALL
#data_stream_ID = [mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,
                  #mavutil.mavlink.MAV_DATA_STREAM_RAW_SENSORS]
data_rate = 1
num_points = 1000

def read_messages(mav_obj):
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
    else:
        print(msg)
    i = 0
    while i < num_points:
        msg = mav_obj.recv_match(blocking=True)
        # if something catches your interest, pull out that msg type
        #msg = mav_obj.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        #msg = mav_obj.recv_match(type='SCALED_IMU2', blocking=True)
        #msg = mav_obj.recv_match(type='RAW_IMU', blocking=True)

        # uncomment if statement for parameters
        #if not(msg.get_msgId() == -1) and msg.name == 'PARAM_VALUE':
            #print(msg)

        print(msg)
        i += 1


mav = mavutil.mavlink_connection(device, baud=11520)
# check that there is a heartbeat
mav.recv_match(type='HEARTBEAT', blocking=True)
print("Heartbeat from APM (system %u component %u)" %
      (mav.target_system, mav.target_component))
print('')


# a try block ensures that mav with always be closed
try:

    mav.mav.request_data_stream_send(mav.target_system,
                                    mav.target_component,
                                    data_stream_ID,
                                    data_rate,
                                    1)

    read_messages(mav)
finally:
    # close the connection
    mav.mav.request_data_stream_send(mav.target_system,
                                    mav.target_component,
                                    data_stream_ID,
                                    data_rate,
                                    0)
    mav.close()
