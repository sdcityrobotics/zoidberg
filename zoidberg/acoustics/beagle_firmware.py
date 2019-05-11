"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import socket
import pyaudio
import numpy as np
from math import pi
import time

# for getting data off the board
HOST = 'localhost'
PORT = 50007

fs = 96000  # sampling frequency

# window specification, this is taken from:
# Heinzel G. et al., “Spectrum and spectral density estimation by the Discrete
# Fourier transform (DFT), including a comprehensive list of window functions
# and some new flat-top windows”

winwidth = int(3 * fs / 1e3)  # 3 ms window
overlap = .598  # a value between 0 and 1, Heinzel's optimal overlap
# sampling positions along a continous stream of data
num_overlap = int(np.ceil(winwidth * overlap))

# precompute window, this math saves an import of scipy :)
nuttall3b = [.4243801, .4973406, .0782793]
fac = np.linspace(-np.pi, np.pi, winwidth)
window = np.zeros(winwidth)
for k in range(len(nuttall3b)):
    window += nuttall3b[k] * np.cos(k * fac)


class BeagleFirmware:
    """Code which will run continously on beagle bone"""
    def __init__(self, fc):
        """Select frequency of interest"""
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
        num_i = int(np.ceil(self.buffer_size / self.num_step))
        self.win_i = np.arange(num_i) * self.num_step

        # positions of the main processing
        no_edge_i = self.win_i < self.buffer_size - self.winwidth
        yes_edge_i = self.win_i > self.buffer_size - self.winwidth

        # change the buffer size to match pre-computated boundries
        self.buffer_size = self.win_i[-1] + self.num_step
        in_buff_i = self.win_i < self.buffer_size
        self.win_i = self.win_i[in_buff_i]
        no_edge_i = no_edge_i[in_buff_i]
        yes_edge_i = yes_edge_i[in_buff_i]

        # main filter is a large matrix that processes all data with no overlap
        main_filter = []
        for wp in self.win_i[no_edge_i]:
            temp = np.zeros(self.buffer_size, dtype=np.complex64)
            temp[wp: wp + self.winwidth] = self.twidle.copy()
            main_filter.append(temp)
        self.main_filter = np.array(main_filter)

        # tail filter is a small matrix that processes data that is overlaped
        self.tail_window_i = self.win_i[yes_edge_i]
        self.tail_size = (self.tail_window_i[-1] + self.winwidth) \
                       - self.tail_window_i[0]
        self.old_tail_size = self.buffer_size - self.tail_window_i[0]
        self.new_tail_size = self.tail_size - self.old_tail_size

        tail_filter = []
        for wp in self.tail_window_i:
            wp -= self.tail_window_i[0]
            temp = np.zeros(self.tail_size, dtype=np.complex64)
            temp[wp:wp + self.winwidth] = self.twidle.copy()
            tail_filter.append(temp)
        self.tail_filter = np.array(tail_filter)

        # create a buffer to save samples needed in overlap correction
        self.old_tail = np.zeros((self.old_tail_size, self.num_channels),
                                 dtype=np.float32)

    def buf_to_np(self, buf):
        """Convert a buffer of bytes to numpy array
        in: 2 channel int24
        out: float32 numpy array"""
        a = np.ndarray(len(buf), np.dtype('<i1'), buf)
        e = np.zeros(int(len(buf) // self.num_bytes), np.dtype('<i4'))
        for i in range(self.num_bytes):
            # e is offset by 1, this makes LSB 0 (up-casting data type)
            e.view(dtype='<i1')[i + 1::4] = a.view(dtype='<i1')[i::3]
        result = np.array(e, dtype='float32') * self.int_to_float
        return result.reshape(-1, self.num_channels)

    def process(self, recorded_data):
        """
        Compute single frequency samples from a recorded time series
        """
        # compute results from tail of previous buffer
        all_tail = np.concatenate([self.old_tail,
                                   recorded_data[:self.new_tail_size, :]])
        # record tail values for next time around
        self.old_tail = recorded_data[self.tail_window_i[0]: ,:].copy()
        tail_atfc = self.tail_filter @ all_tail
        main_atfc = self.main_filter @ recorded_data
        return [tail_atfc, main_atfc]

    def dump(self, processed_data):
        """ dump the data into a socket """
        b1 = processed_data[0].tobytes()
        b2 = processed_data[1].tobytes()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b1)
            s.sendall(b2)

if __name__ == '__main__':
    bb = BeagleFirmware(5000)
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=bb.in_format,
                        channels=bb.num_channels,
                        rate=bb.fs,
                        input_device_index=7,
                        input=True,
                        frames_per_buffer=bb.buffer_size)
        print("* recording")
        ts = time.time()
        frames = []

        for i in range(int(5 * bb.fs / bb.buffer_size)):
            data = stream.read(bb.buffer_size, exception_on_overflow=False)
            asnp = bb.buf_to_np(data)
            p_atfc = bb.process(asnp)
            frames.append(asnp)

        print("* done recording")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
