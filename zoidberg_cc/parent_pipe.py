"""
This node represents a data collection unit. In particular, this is what will
be implimented for the zed camera.
"""

import os, time, sys
import pickle
import numpy as np
from zoidberg import utils

pipe_name = 'pipe_test'

def child():
    if not os.path.exists(pipe_name):
        print("No pipe exists, exiting")
        return

    # generate some fake data
    stamped_data = [utils.timestamp(), np.random.randn(3, 3)]
    outobj = pickle.dumps(stamped_data)

    #Make sure that the pipe is cleared before putting new data out
    try:
        pipe = os.open(pipe_name, os.O_RDONLY | os.O_NONBLOCK)
        line = os.read(pipe, 0)
    except OSError as err:
        print(err)
        if err.errno == 11:
            # this error indicates that the pipe has no data in it
            pass
        else:
            raise err
    finally:
        os.close(pipe)

    # Dump latest data to pipe
    try:
        pipe = os.open(pipe_name, os.O_WRONLY | os.O_NONBLOCK)
        os.write(pipe, outobj)
        os.close(pipe)
    except OSError as err:
        if err.errno == 6:
            # This error indicates no consumer is connected to pipe
            pass
        else:
            raise err

if __name__ == "__main__":
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)
    try:
        while True:
            child()
            time.sleep(.5)
    finally:
        os.unlink(pipe_name)
