from math import copysign
from zoidberg import heading_diff, empty_value

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
