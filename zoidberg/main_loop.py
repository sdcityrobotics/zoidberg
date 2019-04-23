from time import time
from zoidberg import pause

actionperiod = 0.1  # update period, Hz

def main_loop(node_dict, episode_name, timeout, isdone=None, get_x=None,
              get_y=None, get_z=None, get_r=None):
    """Mainloop is common to all mission tasks

    modedict is a dictionary of all instrument nodes. one must be the pixhawk.
    mainloop will run untill timeout
    isdone is a function that will terminate the loop if True
    get functions are called to return motor outputs
    """
    # mark start time of task
    starttime = time()
    while True:
        # mark start time of loop
        currenttime = time()

        for key in node_dict.keys():
            # update all of the nodes in the node dictionary
            node_dict[key].check_readings()
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
            break

        # timeout condition
        if (currenttime - starttime) > timeout:
            break

        pause(currenttime, actionperiod)
