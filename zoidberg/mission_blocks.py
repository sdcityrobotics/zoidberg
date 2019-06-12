"""
==============
Mission blocks
==============
Building blocks used to create behaviors, and slowly build up missions
"""

from time import time
from math import copysign
from zoidberg import heading_diff, empty_value, pause

actionperiod = 0.1  # update period, Hz

def main_loop(node_dict, episode_name, timeout, isdone=None,
              get_x=None, get_y=None, get_z=None, get_r=None,
              detection_task=None):
    """Mainloop is common to all mission tasks

    modedict is a dictionary of all instrument nodes. one must be the pixhawk.
    mainloop will run untill timeout

    isdone: function that will terminate the loop if True
    also used to actuate torpedoes and drop markers. These are performed as
    side effects, i.e. invisible to the user. Be very careful hiding behaviors
    in this way, but for torpedoes we make an exception.

    get functions: called to return motor outputs. The only approved way to
    move the robot around

    detection_task: run on the current image and depth map of the zed node
    populates the detection list in vision node

    """
    # mark start time of task
    starttime = time()
    while True:
        # mark start time of loop
        currenttime = time()

        for key in node_dict.keys():
            # update all of the nodes in the node dictionary
            node_dict[key].check_readings()

        # update detection list in vision node with recent zed image
        if detection_task is not None:
            detection_task(node_dict)

        for key in node_dict.keys():
            # log data for all of the nodes in the node dictionary
            node_dict[key].log(episode_name)

        # compute motor updates
        if get_x is not None:
            vx = get_x(node_dict)
        else:
            vx = 0
        if get_y is not None:
            vy = get_y(node_dict)
        else:
            vy = 0
        if get_z is not None:
            vz = get_z(node_dict)
        else:
            vz = 0
        if get_r is not None:
            vr = get_r(node_dict)
        else:
            vr = 0

        # send motor commands to pixhawk
        node_dict['pn'].send_rc(vel_forward=vx,
                                vel_side=vy,
                                vel_dive=vz,
                                vel_turn=vr)

        # mission completion check
        if isdone(node_dict):
            return True

        # timeout condition
        if (currenttime - starttime) > timeout:
            return False

        pause(currenttime, actionperiod)


def constant_r_task(r_target, P, r_max):
    """return an anonymous function to turn to desired heading"""
    def task(node_dict):
        """return a delta heading value to best turn to heading"""
        # always check that the sensor has been initialized
        if node_dict['pn'].heading == empty_value:
            # if sensor is not reading, return no motor command
            return 0
        # compute heading difference
        hdiff = heading_diff(r_target, node_dict['pn'].heading)
        # p-control
        hout = hdiff * P
        # limit output if necassary
        if abs(hout) > r_max:
            hout = copysign(r_max, hout)
        return hout

    # return the function we just created
    return task


def constant_r_success(r_target, tol):
    """return an anonymous function to test if at desired heading"""
    def isdone(node_dict):
        """return a delta heading value to best turn to heading"""
        # compute heading difference
        hdiff = heading_diff(r_target, node_dict['pn'].heading)
        # return if we are we close enough
        return abs(hdiff) < abs(tol)

    # return the function we just created
    return isdone
