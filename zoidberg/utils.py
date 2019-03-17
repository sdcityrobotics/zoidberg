import os
from time import time, sleep
from datetime import datetime

# standard to indicate a bad reading or unitialized value
empty_value = -9999.

def timestamp(datet=None):
    """create a standard timestamp string
    year_JulianDay_Hour_Min_Sec_MS
    """
    if datet is None:
        datet = datetime.now()
    timestamp = '{0:%y}_{0:%j}_{0:%H}_{0:%M}_{0:%S}_{0:%f}'.format(datet)
    # only return to ms precision
    timestamp = timestamp[:-3]
    return timestamp

def pause(start_time, action_period):
    """Sleep untill next action period"""
    tsleep = start_time + action_period - time()
    if tsleep > 0:
        sleep(tsleep)

def episode():
    """Return a folder name for a mission"""
    savedir = '_'.join(timestamp().split('_')[:-1])
    return 'episode_' + savedir
