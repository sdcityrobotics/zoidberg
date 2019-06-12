"""
==============
Acoustics node
==============
Compute acoustic energy at a single frequency. This is equivalent to computing
a single bin of an discrete fourier transform. This result, p_atfc, can be
compaired across multiple channels to get a bearing estimate, a process called
beamforming.
"""
import numpy as np
from math import pi
import threading
import queue
import pyaudio

fs = 96000  # sampling frequency
buffer_size = 2 ** 12  # power of 2 buffer size, fixed

# window specification, this is taken from:
# Heinzel G. et al., “Spectrum and spectral density estimation by the Discrete
# Fourier transform (DFT), including a comprehensive list of window functions
# and some new flat-top windows”

winwidth = int(2 * fs / 1e3)  # 2 ms window
# make sure winwidth is even
if winwidth % 2 == 1: winwidth += 1

# a value between 0 and 1, Heinzel's optimal overlap between sections
overlap = .598

# rough section positions along a continous stream of data
num_step = int(np.floor(winwidth * (1 - overlap)))

# compute integer number of section positions
num_sections = buffer_size // num_step
section_lengths = np.ones(num_sections, dtype=np.int) * num_step
section_lengths[: buffer_size % num_sections] += 1

# all section with start indicies inside of a buffer
all_i = np.hstack([0, np.cumsum(section_lengths[:-1])])
# index of sections that fit completely inside a buffer
is_complete = all_i + winwidth < buffer_size
main_i = all_i[is_complete]
# index of sections that fit only partially inside a buffer
tail_i = all_i[np.bitwise_not(is_complete)]

# precompute window, this math saves an import of scipy :)
nuttall3b = [.4243801, .4973406, .0782793]
fac = np.linspace(-np.pi, np.pi, winwidth)
window = np.zeros(winwidth)
for k in range(len(nuttall3b)):
    window += nuttall3b[k] * np.cos(k * fac)

class AcousticsNode:
    """Compute single frequency result continously, beamform at each ping"""
    def __init__(self, fc):
        """fc is frequency of interest"""
        # center frequency that we are looking for
        self.fc = fc

        # ADC data conversion stuff
        self.fs = fs
        self.buffer_size = buffer_size
        self.in_format = pyaudio.paInt24
        self.num_channels = 3
        self.num_bytes = 3

        # Convert values to -1, 1 range
        in_range = 2 ** (8 * self.num_bytes - 1)
        self.int_to_float = 1 / in_range

        # decimation of the input data. Processing happens on chuncks of data
        self.window = window
        self.winwidth = winwidth
        # number of samples to move each calculation
        self.num_step = num_step

        # precompute twidle factors
        # https://forum.bela.io/d/799-high-frequency-narrow-banded-beamforming
        self.twidle = np.exp(-1j * 2 * pi * self.fc / self.fs
                             * np.arange(self.winwidth))
        self.twidle *= self.window
        self.twidle.astype(np.complex64)

        # main filter is a large matrix that processes all data with no overlap
        main_filter = []
        for mi in main_i:
            temp = np.zeros(buffer_size, dtype=np.complex64)
            temp[mi: mi + self.winwidth] = self.twidle.copy()
            main_filter.append(temp)
        self.main_filter = np.array(main_filter)

        # tail filter is a small matrix that processes data that is overlaped
        self.tail_size = tail_i[-1] + winwidth
        self.old_tail_size = self.buffer_size - tail_i[0]
        self.new_tail_size = self.tail_size - self.old_tail_size

        tail_filter = []
        for mi in tail_i - tail_i[0]:
            temp = np.zeros(self.tail_size, dtype=np.complex64)
            temp[mi: mi + self.winwidth] = self.twidle.copy()
            tail_filter.append(temp)
        self.tail_filter = np.array(tail_filter)

        # create a buffer to save samples needed in overlap correction
        self.old_tail = np.zeros((self.old_tail_size, self.num_channels),
                                 dtype=np.float32)

    def process(self, recorded_data):
        """
        Compute single frequency samples from a recorded time series
        """
        # compute results from tail of previous buffer
        all_tail = np.concatenate([self.old_tail,
                                   recorded_data[:self.new_tail_size, :]])
        # compute acoustic values as a vector multiply
        tail_atfc = self.tail_filter @ all_tail
        main_atfc = self.main_filter @ recorded_data
        # record tail values for next time around
        self.old_tail = recorded_data[self.tail_index[0]: ,:].copy()
        return np.concatenate([tail_atfc, main_atfc])

    def log(self, episode_name):
        """save current reading to a log file"""
        if not os.path.isdir(episode_name):
            os.makedirs(episode_name)
        save_name = os.path.join(episode_name, 'acoustics.dat')

        with open(save_name, 'ab+') as f:
            f.write(self.curr_read.tobytes())

    def load(self, episode_name):
        """load from log file to current reading"""
        with open(savefile, 'rb') as f:
            bytesin = f.read()

        tout = np.frombuffer(bytesin, dtype=self.datatype)
        tout = tout.reshape((-1, num_channels))
        self.all_read = tout

    def _buf_to_np(self, buf):
        """Convert a buffer of bytes to numpy array
        in: N channel int24 buffer
        out: float32 numpy array"""
        a = np.ndarray(len(buf), np.dtype('<i1'), buf)
        e = np.zeros(int(len(buf) // self.num_bytes), np.dtype('<i4'))
        for i in range(self.num_bytes):
            # e is offset by 1, this makes LSB 0 (up-casting data type)
            e.view(dtype='<i1')[i + 1::4] = a.view(dtype='<i1')[i::3]
        result = np.array(e, dtype='float32') * self.int_to_float
        return result.reshape(-1, self.num_channels)
