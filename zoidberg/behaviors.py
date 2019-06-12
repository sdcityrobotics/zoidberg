"""
=========
Behaviors
=========
Concise things that zoidberg does in the course of a mission
"""

from zoidberg import mission_blocks

turn_P = 3  # proportionality constant for turning
turn_max = 70  # max rate of turn, percentage. 0 < turn_max < 100
turn_tol = 5  # tolerance of turning. Turn is sucsessful at this error

def change_heading(node_dict, runnum, total_time, target_heading):
    """Turn to specified heading"""
    # setup proportional control
    r_task = mission_blocks.constant_r_task(target_heading, turn_P, turn_max)
    # setup success metric
    r_succ = mission_blocks.constant_r_success(target_heading, turn_tol)
    # send robot off on a loop
    istimeout = mission_blocks.main_loop(node_dict,
                                         runnum,
                                         total_time,
                                         isdone=r_succ,
                                         get_r=r_task)
    # return loop result
    return istimeout
