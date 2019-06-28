"""
===============
Beagle firmware
===============
Compute acoustic energy at a single frequency. This is equivalent to computing
a single bin of an discrete fourier transform. This result, p_atfc, can be
compaired across multiple channels to get a bearing estimate, a process called
beamforming.
"""
import numpy as np
from math import pi
from scipy.signal import stft
import matplotlib.pyplot as plt

import bearing_simulation
import beagle_firmware
import acoustics_node

cmap = plt.cm.magma_r
cmap.set_under('w')

all_data = list(bearing_simulation.get_buffer())
all_data = np.concatenate(all_data, axis=1)

window = beagle_firmware.window

an = acoustics_node.AcousticsNode(bearing_simulation.fc)

f, t, p_ft = stft(all_data, window=window,
                     nperseg=window.size, fs=96000,
                     noverlap=window.size - beagle_firmware.num_step)

pdB = 20 * np.log10(np.abs(p_ft))
pdB -= np.max(pdB)

tploti = t > 45

fig, ax = plt.subplots()
cm = ax.pcolormesh(t[tploti], f / 1e3, pdB[0, :, tploti].T, vmin=-30, rasterized=True,
                   cmap=cmap)
ax.set_ylabel('Frequency, kHz')
ax.set_xlabel('time, s')

num_pings = 50
byping = np.array_split(p_ft, num_pings, axis=2)
Bs = []
for p in byping:
    testi = np.argmax(p)
    _, fi, testi = np.unravel_index(testi, p.shape)
    p_comp = p[:, fi, testi]
    K = np.outer(np.conj(p_comp), p_comp)
    B = np.sum((np.conj(an.look_vectors).T @ K) * an.look_vectors.T, axis=1)
    Bs.append(B)

Bs = np.array(Bs)
b_dB = 20 * np.log10(np.abs(Bs))
b_dB -= np.max(b_dB)

fig, ax = plt.subplots()
for i in np.arange(5) * 8:
    ax.plot(an.look_directions, np.abs(Bs[i, :]), 'k')
    tb = np.radians(bearing_simulation.test_bearings[i])
    ax.plot([tb, tb], [0, 0.1], color='0.6')


