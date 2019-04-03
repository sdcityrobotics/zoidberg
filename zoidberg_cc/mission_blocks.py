from math import copysign

def constant_r_task(r_target, P, r_max):
    """return an anonymous function to turn to desired heading"""
    def task(node_dict):
        """return a delta heading value to best turn to heading"""
        # compute heading difference
        hdiff = r_target - node_dict['pn'].heading
        # handle 0/360 change at magnetic north
        if abs(hdiff) > 180:
            if hdiff < 0:
                hdiff += 360
            else:
                hdiff -= 360
        # p-control
        hout = hdiff * P
        # limit output if necassary
        if abs(hout) > r_max:
            hout = copysign(r_max, hout)
        return hout
    return task

def constant_r_success(r_target, tol):
    """return an anonymous function to test if at desired heading"""
    def isdone(node_dict):
        """return a delta heading value to best turn to heading"""
        # compute heading difference
        hdiff = r_target - node_dict['pn'].heading
        # handle 0/360 change at magnetic north
        if abs(hdiff) > 180:
            if hdiff < 0:
                hdiff += 360
            else:
                hdiff -= 360
        # return if we are we close enough
        return abs(hdiff) < abs(tol)
    return isdone
