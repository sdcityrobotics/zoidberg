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

def write_pipe(pipe_name, byte_stream):
    """write byte_stream to pipe, clears any existing data in pipe before write
    """
    # check that the pipe exists
    if not os.path.exists(pipe_name):
        print("No pipe exists, exiting")
        return

    #Make sure that the pipe is cleared before putting new data out
    try:
        pipe = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
        line = os.read(pipe, 0)
    except OSError as err:
        # assume this error indicates that the pipe has no data in it
        pass
    finally:
        os.close(pipe)

    # Dump latest data to pipe
    try:
        pipe = os.open(pipe_name, os.O_WRONLY | os.O_NONBLOCK)
        os.write(pipe, byte_stream)
    except OSError as err:
        # assumes this error indicates no consumer is connected to pipe
        pass
    finally:
        os.close(pipe)
