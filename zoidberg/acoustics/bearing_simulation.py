import numpy as np
from math import pi, sin, cos, radians
from scipy.interpolate import interp1d
from scipy.signal.windows import hann
import matplotlib.pyplot as plt
from time import sleep

from beagle_firmware import BeagleFirmware

plt.ion()

# These paramters are expected to be mostly constant, fixed by competition
channel_depth = 5
source_depth = 4.5
fs = 96000
fc = 30000
T = 0.004  # pulse width, ms
c = 1480.  #speed of sound

# Array geometry
num_channels = 3
#array_position = np.array([0, c / (2 * fc), c / fc])
array_position = np.array([0, 0.0185, 0.037])

# add some noise to the signal. We can't anticipate what the tank will sound
# like in the background, so this is a coarse approximation of background
# interference
noise_level = 1e-5  # white noise variance. play around with this number

# generate a range of potential bearings
num_b = 50
test_bearings = np.arange(num_b) * 180 / num_b - 90

def one_ping(rcr_range, rcr_depth, rcr_bearing):
    """one second of simulated data, single ping at specified range and bearing
    """
    # time axis of simulated recorded signal
    taxis = np.arange(fs) / fs  # one second of data
    start_i = 300  # small offset for plotting purposes

    # each receiver will have a slighly different coordinates based on bearing and
    # distance
    dx = rcr_range + array_position * sin(radians(rcr_bearing))
    dy = array_position * cos(radians(rcr_bearing))
    rr = np.sqrt(dx ** 2 + dy ** 2)

    # simulate first 3 in-plane arrivals
    r_dir = np.sqrt(rr ** 2 + (rcr_depth - source_depth) ** 2)
    r_surf = np.sqrt(rr ** 2 + (rcr_depth + source_depth) ** 2)
    r_bottom = np.sqrt(rr ** 2 + (2 * channel_depth - source_depth) ** 2)

    # time of arrival
    time_dir = r_dir / c
    time_surf = r_surf / c
    time_bottom = r_bottom / c

    # transmitted signal
    tsig = np.arange(np.ceil(T * fs)) / fs
    sig_xmitt = np.sin(2 * pi * fc * tsig)
    sig_xmitt *= hann(tsig.size)
    # create an interpolator, this allows for sub sample timing of arrivals
    sig_ier = interp1d(tsig,
                       sig_xmitt,
                       kind=3,
                       bounds_error=False,
                       fill_value=0.)

    # create time series as a sum of all arrivals
    x_sig = np.zeros((num_channels, taxis.size), dtype=np.float_)
    x_sig += sig_ier(taxis - time_dir[:, None]) / r_dir[:, None]
    x_sig -= sig_ier(taxis - time_surf[:, None]) / r_surf[:, None]
    x_sig -= sig_ier(taxis - time_bottom[:, None]) / r_bottom[:, None]

    # create some noise on all channels
    x_sig += np.random.randn(*x_sig.shape) * np.sqrt(noise_level)
    return x_sig

def get_buffer():
    """Get a single buffer, bearing will slowly change with pings"""
    currdata = []
    for tb in test_bearings:
        currdata.append(one_ping(10, 3, tb))
        all_data = np.concatenate(currdata, axis=1)
        num_blocks = all_data.shape[1] // nbd.buffer_size
        block_data = all_data[:, :num_blocks * nbd.buffer_size].copy()
        block_data = np.split(block_data, num_blocks, axis=1)
        currdata = [all_data[:, num_blocks * nbd.buffer_size + 1:]]
        for block in block_data:
            yield block

# start up firware node
nbd = BeagleFirmware(fc, sim_gen=get_buffer())

if __name__ == "__main__":
    while True:
        nbd.spin()
        sleep(0.01)
