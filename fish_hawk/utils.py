from time import time, sleep
from datetime import datetime

def date_string():
    """Spit back current time information as string (large scale time)"""
    now = datetime.now()
    # returns unique time identifier down to second level
    return now.strftime('__%d_%m_%y__%H_%M_%S')

def timestamp():
    """create a timestamp from midnight in milliseconds"""
    timestamp = int(time() * 1000)
    return timestamp

def pause(start_time, action_period):
    """Sleep untill next action period"""
    tsleep = start_time + action_period - time()
    if tsleep > 0:
        sleep(tsleep)
