import numpy as np
from scipy.signal.windows import hann, general_cosine
from scipy.interpolate import interp1d
from math import sqrt, pi
import matplotlib.pyplot as plt

fs = 96000
fc = 30000
T = 0.004  # pulse width, ms

c = 1500.  #speed of sound
winwidth = 96  # processing widow length, make a multiple of 96

channel_depth = 5
source_depth = 4.5
receiver_depth = 3
receiver_range = 10

# simulate first 3 in-plane arriavals
r_dir = sqrt(receiver_range ** 2 + (receiver_depth - source_depth) ** 2)
r_surf = sqrt(receiver_range ** 2 + (receiver_depth + source_depth) ** 2)
r_bottom = sqrt(receiver_range ** 2 + (2 * channel_depth - source_depth) ** 2)

time_dir = r_dir / c
time_surf = r_surf / c
time_bottom = r_bottom / c

taxis = np.arange(2 ** 10) / fs
taxis += time_dir - winwidth / (fs * 2)

tsig = np.arange(np.ceil(T * fs)) / fs
sig_xmitt = np.sin(2 * pi * fc * tsig)
sig_xmitt *= hann(tsig.size)

# create an interpolator
sig_ier = interp1d(tsig, sig_xmitt, kind=3, bounds_error=False, fill_value=0.)

# create time series as a sum of all arrivals
x_sig = np.zeros_like(taxis)
x_sig += sig_ier(taxis - time_dir) / r_dir
x_sig -= sig_ier(taxis - time_surf) / r_surf
x_sig -= sig_ier(taxis - time_bottom) / r_bottom

# this is really not necassary, but this is a good window

nuttall4c = [0.3635819, 0.4891775, 0.1365995, 0.0106411]
window = general_cosine(winwidth, nuttall4c, sym=False)
num_overlap = int(np.ceil(winwidth * .656))

num_windows = int(np.floor((taxis.size - winwidth) / num_overlap))
win_position = np.arange(num_windows) * num_overlap

sig_FT = []
for wp in win_position:
    sig_FT.append(np.fft.rfft(x_sig[wp: wp + winwidth] * window))

sig_FT = np.array(sig_FT)
win_time = (win_position + winwidth / 2) / fs
win_time += taxis[0]

faxis = np.arange(winwidth // 2 + 1) / winwidth * fs
fbin = int(np.argmin(np.abs(faxis - fc)))

fig, ax = plt.subplots()
ax.plot(taxis, x_sig)
ax.grid()
ax.set_xlabel('time, (s)')
ax.set_xlabel('pressure')
ax.set_title('simulated pressure arrival')

fig, ax = plt.subplots()
ax.plot(win_time, np.abs(sig_FT[:, fbin].T) ** 2)
ax.grid()
ax.set_xlabel('time, (s)')
ax.set_ylabel('$|p|^2$')
ax.set_title('arrival energy, time series')

plt.show(block=False)
