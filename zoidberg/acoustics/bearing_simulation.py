import numpy as np
from math import pi, sin, cos, radians
from scipy.interpolate import interp1d
from scipy.signal.windows import hann
import matplotlib.pyplot as plt

from beagle_firmware import BeagleFirmware

# These paramters are expected to be mostly constant, fixed by competition
channel_depth = 5
source_depth = 4.5
fs = 96000
fc = 30000
T = 0.004  # pulse width, ms
c = 1480.  #speed of sound

# signal threshold value. Once this is exceeded we begin beamforming
p2_thresh = .025

# these will change all the time, and can be played with (within reason)
num_channels = 3
channel_coord = np.array([0, c / (2 * fc), c / fc])
receiver_depth = 4.5
receiver_range = 1  # range to channel at 0 coordinate point
receiver_bearing = -30 # bearing, degrees. Between -90 and 90

# add some noise to the signal. We can't anticipate what the tank will sound
# like in the background, so this is a coarse approximation of background
# interference
noise_level = 1e-5  # white noise variance. play around with this number

# each receiver will have a slighly different coordinates based on bearing and
# distance
dx = receiver_range + channel_coord * sin(radians(receiver_bearing))
dy = receiver_range + channel_coord * cos(radians(receiver_bearing))
rr = np.sqrt(dx ** 2 + dy ** 2)

# simulate first 3 in-plane arrivals
r_dir = np.sqrt(rr ** 2 + (receiver_depth - source_depth) ** 2)
r_surf = np.sqrt(rr ** 2 + (receiver_depth + source_depth) ** 2)
r_bottom = np.sqrt(rr ** 2 + (2 * channel_depth - source_depth) ** 2)

# time of arrival
time_dir = r_dir / c
time_surf = r_surf / c
time_bottom = r_bottom / c

# time axis of simulated recorded signal
taxis = np.arange(2 ** 13) / fs
taxis += time_dir[0] - 300 / fs  # small offset for plotting purposes

# transmitted signal
tsig = np.arange(np.ceil(T * fs)) / fs
sig_xmitt = np.sin(2 * pi * fc * tsig)
sig_xmitt *= hann(tsig.size)
# create an interpolator, this allows for sub sample timing of arrivals
sig_ier = interp1d(tsig, sig_xmitt, kind=3, bounds_error=False, fill_value=0.)

# create time series as a sum of all arrivals
x_sig = np.zeros((taxis.size, num_channels), dtype=np.float_)
x_sig += sig_ier(taxis[:, None] - time_dir) / r_dir
x_sig -= sig_ier(taxis[:, None] - time_surf) / r_surf
x_sig -= sig_ier(taxis[:, None] - time_bottom) / r_bottom

# create some noise on all channels
x_sig += np.random.randn(*x_sig.shape) * np.sqrt(noise_level)

nbd = BeagleFirmware(fc)

# compute output on each channel as though it came from the hydrophones
starti = 0
buffer_size = nbd.buffer_size
num_buffer = int(np.floor(x_sig.shape[0] / buffer_size))
buff_i = np.arange(num_buffer) * buffer_size

out_data = []
for i in buff_i:
    p_atfc = nbd.process(x_sig[i: i + buffer_size, :])
    out_data.append(np.concatenate(p_atfc))

out_data = np.concatenate(out_data)

# scale the data to V peak
out_data = np.sqrt(2) * np.sqrt(2 * np.abs(out_data) ** 2 / np.sum(nbd.window) ** 2)
win_time = np.arange(out_data.shape[0]) * nbd.num_step / fs + taxis[0]

fig, ax = plt.subplots()
ax.plot(taxis * 1e3, x_sig)
ax.plot([-1e4, 1e4], [1, 1], color='C3', label='clipping threshold')
ax.plot([-1e4, 1e4], [-1, -1], color='C3')
ax.grid()
ax.legend()
ax.set_xlim(taxis[0] * 1e3, taxis[-1] * 1e3)
ax.set_xlabel('time, (ms)')
ax.set_ylabel('pressure')
ax.set_title('simulated pressure arrival')

fig, ax = plt.subplots()
ax.plot(win_time * 1e3, out_data)
ax.plot([-1e4, 1e4], [p2_thresh, p2_thresh], 'k', label='detection threshold')
ax.plot([-1e4, 1e4], [1, 1], color='C3', label='clipping threshold')
ax.grid()
ax.legend()
ax.set_xlim(win_time[0] * 1e3, win_time[-1] * 1e3)
ax.set_xlabel('time, (ms)')
ax.set_ylabel('$|p|^2$')
ax.set_title('arrival energy at {:d} kHz, time series'.format(int(fc / 1e3)))

plt.show(block=False)
