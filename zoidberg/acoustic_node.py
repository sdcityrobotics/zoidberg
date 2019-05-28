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
buffer_size = 2 ** 12  # jack audio requires a power of 2 buffer size

# window specification, this is taken from:
# Heinzel G. et al., “Spectrum and spectral density estimation by the Discrete
# Fourier transform (DFT), including a comprehensive list of window functions
# and some new flat-top windows”

winwidth = int(2 * fs / 1e3)  # 2 ms window
overlap = .598  # a value between 0 and 1, Heinzel's optimal overlap
# sampling positions along a continous stream of data
num_overlap = int(np.ceil(winwidth * overlap))

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
        self.buffer_size = 1024 * 4
        self.in_format = pyaudio.paInt24
        self.num_channels = 3
        self.num_bytes = 3

        # Convert values to -1, 1 range
        in_range = 2 ** (8 * self.num_bytes - 1)
        self.int_to_float = 1 / in_range

        # decimation of the input data. Processing happens on chuncks of data
        self.buffer_size = buffer_size
        self.window = window
        self.winwidth = winwidth
        # number of samples to move each calculation
        self.num_step = self.winwidth - num_overlap

        # precompute twidle factors
        # https://forum.bela.io/d/799-high-frequency-narrow-banded-beamforming
        self.twidle = np.exp(-1j * 2 * pi * self.fc / self.fs
                             * np.arange(self.winwidth))
        self.twidle *= self.window
        self.twidle.astype(np.complex64)

        # compute where the sampling will lie in each buffer
        # adjust window edges so that we end on a buffer length
        num_i = int(np.round((buffer_size - winwidth) / self.num_step))
        nominal_step = (buffer_size - winwidth) // num_i
        remain_step = (buffer_size - winwidth) % num_i
        # compute length of each step. This is not constant to make sure we end
        # at a buffer length
        steps = np.ones(num_i, dtype=np.int) * nominal_step
        if remain_step > num_i:
            print('got to a negative factor')
            steps[: (num_i - remain_step)] -= 1
        else:
            steps[: remain_step] += 1

        # compute the sampling positions in the buffer. These are the main
        # sampling points, because they can be computed without waiting for the
        # next buffer
        win_i = [0]
        for s in steps:
            win_i.append(win_i[-1] + s)
        main_filter_positions = np.array(win_i)

        # compute tail indicies. These are samples that can not be computed
        # untill the next buffer is collected because they go over the edge
        num_tail = winwidth // self.num_step
        for ti in range(num_tail):
            win_i.append(win_i[-1] + nominal_step)
        # compute the position of the tail indicies
        self.tail_index = np.array(win_i[-num_tail: ])
        # all indicies for processing
        self.win_i = np.array(win_i)

        # main filter is a large matrix that processes all data with no overlap
        main_filter = []
        for wp in main_filter_positions:
            temp = np.zeros(buffer_size, dtype=np.complex64)
            temp[wp: wp + self.winwidth] = self.twidle.copy()
            main_filter.append(temp)
        self.main_filter = np.array(main_filter)

        # tail filter is a small matrix that processes data that is overlaped
        self.tail_size = (num_tail - 1) * nominal_step + self.winwidth
        self.old_tail_size = self.winwidth - nominal_step
        self.new_tail_size = self.tail_size - self.old_tail_size

        tail_filter = []
        for wp in np.arange(num_tail) * nominal_step:
            temp = np.zeros(self.tail_size, dtype=np.complex64)
            temp[wp: wp + self.winwidth] = self.twidle.copy()
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
        return np.hstack([tail_atfc, main_atfc])

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
