"""
This node represents a data processing unit.

It is important that this works
the same way in two cases: when processing is faster than data collection, and
when processing is slower than data collection. In both cases this node expects
to read the latest data reading, and only the latest data reading, each time
it checks the pipe
"""

import os, time, sys
import pickle
import numpy as np

pipe_name = 'pipe_test'

def parent():
    with open(pipe_name, 'rb') as infile:
        line = infile.read()
        data_out = pickle.loads(line)
        print(data_out[0])
        print(data_out[1])

if __name__=="__main__":
    for _ in range(10):
        parent()
        time.sleep(.001)
