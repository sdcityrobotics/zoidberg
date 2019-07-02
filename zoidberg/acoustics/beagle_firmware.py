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
import pyaudio
import lcm

from zoidberg_lcm import audio_data_t
from zoidberg import timestamp


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

class BeagleFirmware:
    """Compute single frequency result continously, beamform at each ping"""
    def __init__(self, fc, sim_gen=None):
        """fc is frequency of interest
        sim_gen is a generater object used for simulation. Each time next()
        is called on it, it is expected to return a buffer like array
        """
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
        self.main_filter = np.array(main_filter).T

        # tail filter is a small matrix that processes data that is overlaped
        self.old_tail_size = self.buffer_size - tail_i[0]
        self.tail_size = self.old_tail_size + winwidth
        self.new_tail_size = self.tail_size - self.old_tail_size

        tail_filter = []
        for mi in tail_i - tail_i[0]:
            temp = np.zeros(self.tail_size, dtype=np.complex64)
            temp[mi: mi + self.winwidth] = self.twidle.copy()
            tail_filter.append(temp)
        self.tail_filter = np.array(tail_filter).T

        # create a buffer to save samples needed in overlap correction
        self.old_tail = np.zeros((self.num_channels, self.old_tail_size),
                                 dtype=np.float32)

        # pyaudio and LCM setup
        self.sim_gen = sim_gen
        self.p = None
        self.stream = None
        self.lc = lcm.LCM()

    def isactive(self, to_arm):
        """startup or shutdown data stream from audio card"""
        if self.sim_gen is None:
            return

        if to_arm:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=self.in_format,
                                      channels=self.num_channels,
                                      rate=self.fc,
                                      input=True,
                                      frames_per_buffer=self.buffer_size)
        else:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate

    def spin(self):
        """Process one frame at a time, put into an infinite loop"""
        if self.sim_gen is None:
            # read data from stream object and process it
            data = self.stream.read(self.buffer_size)
            recorded_data = self._buf_to_np(data)
        else:
            # pull next record for generator
            recorded_data = next(self.sim_gen)

        processed_data = self.process(recorded_data)
        # send result out over lcm
        msg = audio_data_t()
        msg.timestamp = timestamp()
        msg.num_channels, msg.num_samples = processed_data.shape
        msg.fc = self.fc
        msg.num_step = self.num_step
        msg.fs = self.fs
        msg.re_samples = processed_data.real
        msg.im_samples = processed_data.imag
        self.lc.publish("ACOUSTICS", msg.encode())

    def process(self, recorded_data):
        """
        Compute single frequency samples from a recorded time series
        """
        # compute results from tail of previous buffer
        all_tail = np.concatenate([self.old_tail,
                                   recorded_data[:, :self.new_tail_size]],
                                   axis=1)
        # compute acoustic values as a vector multiply
        tail_atfc = all_tail @ self.tail_filter
        main_atfc = recorded_data @ self.main_filter
        # record tail values for next time around
        self.old_tail = recorded_data[:, -self.old_tail_size:].copy()
        return np.concatenate([tail_atfc, main_atfc], axis=1)

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
