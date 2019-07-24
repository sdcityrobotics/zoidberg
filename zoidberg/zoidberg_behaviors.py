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

dive_P = 30  # proportionality constant for diving
dive_max = 70  # max rate of dive, percentage. 0 < dive_max < 100
dive_tol = .1  # tolerance of dive. Turn is sucsessful at this error

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

def change_depth(node_dict, runnum, total_time, target_depth):
    """Turn to specified heading"""
    # setup proportional control
    z_task = mission_blocks.constant_depth_task(target_depth, dive_P, dive_max)
    # setup success metric
    z_succ = mission_blocks.constant_z_success(target_depth, dive_tol)
    # send robot off on a loop
    istimeout = mission_blocks.main_loop(node_dict,
                                         runnum,
                                         total_time,
                                         isdone=z_succ,
                                         get_z=z_task)
    # return loop result
    return istimeout

def drive_robot(node_dict, runnum, total_time, speed_forward=0, speed_side=0):
    """drive robot at a constant speed untill timeout"""
    surge = mission_blocks.constant_motor_task(speed_forward)
    strafe = mission_blocks.constant_motor_task(speed_side)
    istimeout = mission_blocks.main_loop(node_dict,
                                         runnum,
                                         total_time,
                                         get_x=surge,
                                         get_y=strafe)
    # return loop result
    return istimeout
