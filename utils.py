from time import time, sleep

def timestamp():
    """create a timestamp from midnight in milliseconds"""
    timestamp = int(time() * 1000)
    return timestamp

def pause(start_time, action_period):
    """Sleep untill next action period"""
    tsleep = start_time + update_period - time()
    if tsleep > 0:
        sleep(tsleep)
