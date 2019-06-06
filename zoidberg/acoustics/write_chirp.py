
"""PyAudio Example: Play a WAVE file."""

import pyaudio
import wave
import sys
import numpy as np
from math import pi
from scipy.signal.windows import hann

CHUNK = 1024

p = pyaudio.PyAudio()

fc = 2000

fs = 44100
# time axis of simulated recorded signal
taxis = np.arange(fs) / fs
T = 500 * 1e-3
winwidth = T * fs  # processing widow length, make a multiple of 96

# transmitted signal
tsig = np.arange(np.ceil(T * fs)) / fs
sig_xmitt = np.sin(2 * pi * fc * tsig)
sig_xmitt *= hann(tsig.size)
sig_xmitt.astype(np.float32)
sig_xmitt = np.array([sig_xmitt, sig_xmitt])

stream = p.open(format=pyaudio.paFloat32,
                         channels=2,
                         rate=fs,
                         output=True,
                         )

data = sig_xmitt.tostring()

stream.write(data)

stream.stop_stream()
stream.close()

p.terminate()
