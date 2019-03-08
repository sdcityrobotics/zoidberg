import sounddevice as sd
import numpy as np
from math import pi
from queue import Queue
import matplotlib.pyplot as plt
from ua101_node import UA101
from probe_signal import NarrowBand

fc = 5000  # Hz
bw = 500
fs = 96e3

record_threshold = 1  # not used in simulation

xmitt = NarrowBand(fc, bw, fs)
ua = UA101(fc, record_threshold)

fig, ax = plt.subplots()

plt.show(block=False)
