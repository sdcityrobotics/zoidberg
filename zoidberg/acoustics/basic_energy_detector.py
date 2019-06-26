import numpy as np
from scipy.signal.windows import hann, kaiser
from scipy.interpolate import interp1d
from math import sqrt, pi
import matplotlib.pyplot as plt


# These paramters are expected to be mostly constant, fixed by competition
channel_depth = 5
source_depth = 4.5
fs = 96000
fc = 30000
T = 0.004  # pulse width, ms
c = 1480.  #speed of sound

# Width of filter length, longer filters have better noise rejection, but
# require more overlap in time
winwidth = 2 * 96  # processing widow length, make a multiple of 96
overlap = 0.7  # a value less between 0 and 1

# these will change all the time, and can be played with (within reason)
receiver_depth = 4.5
receiver_range = 1

# add some noise to the signal. We can't anticipate what the tank will sound
# like in the background, so this is a coarse approximation of background
# interference
noise_level = 1e-5  # white noise variance. play around with this number

# signal threshold value. Once this is exceeded we begin beamforming
p2_thresh = .025

# simulate first 3 in-plane arrivals
r_dir = sqrt(receiver_range ** 2 + (receiver_depth - source_depth) ** 2)
r_surf = sqrt(receiver_range ** 2 + (receiver_depth + source_depth) ** 2)
r_bottom = sqrt(receiver_range ** 2 + (2 * channel_depth - source_depth) ** 2)

# time of arrival
time_dir = r_dir / c
time_surf = r_surf / c
time_bottom = r_bottom / c

# time axis of simulated recorded signal
taxis = np.arange(2 ** 11) / fs
taxis += time_dir - 3 * winwidth / (fs * 2)

# transmitted signal
tsig = np.arange(np.ceil(T * fs)) / fs
sig_xmitt = np.sin(2 * pi * fc * tsig)
sig_xmitt *= hann(tsig.size)
# create an interpolator, this allows for sub sample timing of arrivals
sig_ier = interp1d(tsig, sig_xmitt, kind=3, bounds_error=False, fill_value=0.)

# create time series as a sum of all arrivals
x_sig = np.zeros_like(taxis)
x_sig += sig_ier(taxis - time_dir) / r_dir
x_sig -= sig_ier(taxis - time_surf) / r_surf
x_sig -= sig_ier(taxis - time_bottom) / r_bottom

# create some noise
x_sig += np.random.randn(x_sig.size) * np.sqrt(noise_level)

# construct a window for the FFT. This is necassary when we don't know where
# the edges of the signal will be.
window = kaiser(winwidth, 2.5 * pi)
num_overlap = int(np.ceil(winwidth * overlap))

# construct a time axis for the single frequency power
num_windows = int(np.floor((taxis.size - winwidth) / (winwidth - num_overlap)))
win_position = np.arange(num_windows) * (winwidth - num_overlap)
win_time = (win_position + winwidth / 2) / fs
win_time += taxis[0]

# take a sliding position FFT. This will be done on the DSP processing board.
# This is used to extract the single frequency content of the signal over time
sig_FT = []
for wp in win_position:
    sig_FT.append(np.fft.rfft(x_sig[wp: wp + winwidth] * window))
sig_FT = np.array(sig_FT)
faxis = np.arange(winwidth // 2 + 1) / winwidth * fs

# the single bin of the transmitted signal
fbin = int(np.argmin(np.abs(faxis - fc)))
p_FT = sig_FT[:, fbin]
# scale p_FT to original units
p_FT = np.sqrt(2) * np.sqrt(2 * np.abs(p_FT) ** 2 / np.sum(window) ** 2)

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
ax.plot(win_time * 1e3, p_FT)
ax.plot([-1e4, 1e4], [p2_thresh, p2_thresh], 'k', label='detection threshold')
ax.plot([-1e4, 1e4], [1, 1], color='C3', label='clipping threshold')
ax.grid()
ax.legend()
ax.set_xlim(win_time[0] * 1e3, win_time[-1] * 1e3)
ax.set_xlabel('time, (ms)')
ax.set_ylabel('$|p|^2$')
ax.set_title('arrival energy at {:d} kHz, time series'.format(int(fc / 1e3)))

plt.show(block=False)
