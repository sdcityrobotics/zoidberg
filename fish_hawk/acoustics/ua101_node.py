import sounddevice as sd
import numpy as np
from math import pi
from queue import Queue
import matplotlib.pyplot as plt
from scipy.signal import firwin, convolve, resample

class UA101:
    """Open an I/O interface with a UA101"""
    def __init__(self, fc, record_threshold):
        """Basic setup"""
        # can specify one or more center frequencies
        self.fc = np.array(fc, ndmin=1)
        self.record_threshold = record_threshold
        self.blocksize = 4096  # record and write size
        self.numblocks = 16
        self.bw = 500
        # sound device setup
        # find UA-101
        all_devs = sd.query_devices()
        ua_101_dev = [d for d in all_devs if 'UA-101' in d['name']]
        if len(ua_101_dev) == 1:
            self.deviceID = ua_101_dev[0]['name']
        else:
            raise(ValueError('UA-101 device not properly identified'))
        # remaining sd information
        self.channels = 2
        self.samplerate = int(ua_101_dev[0]['default_samplerate'])

        self.NFFT = 2 * self.blocksize
        self.faxis = np.arange(self.NFFT) / self.NFFT
        self.faxis *= self.samplerate

        # index of frequencies of interest
        self.fci = np.zeros(self.faxis.size, dtype=np.bool_)
        # used to go from an excedence to strongest center frequency
        self._fci_inverse = []
        for fc in self.fc:
            fci = np.bitwise_and(self.faxis > fc - self.bw,
                                 self.faxis < fc + self.bw)
            self._fci_inverse = np.ones(np.sum(fci)) * fc
            self.fci = np.bitwise_or(self.fci, fci)
        self._lastdata = Queue()
        self._all_data = Queue()
        self.last_center = None
        self.status = None

    def record(self):
        """open a callback stream with UA101"""
        self.is_exceed = False
        kwargs = dict(samplerate=self.samplerate,
                       blocksize=self.blocksize,
                       device=self.deviceID,
                       channels=self.channels,
                       dtype='float32',
                       callback=self._callback)
        with sd.Stream(**kwargs) as s:
            while s.active:
                sd.sleep(int(100))

        # stack record in a single numpy array
        recorded_data = []
        while not self._all_data.qsize() == 0:
            recorded_data.append(self._all_data.get())
        recorded_data = np.concatenate(recorded_data)
        # empty out last data queue
        while not self._lastdata.qsize() == 0:
            self._lastdata.get()
        return recorded_data

    def _callback(self, indata, outdata, frames, time, status):
        """Check each block for excedence in frequencies of interest"""
        if status:
            self.status = status

        outdata.fill(0)
        curr_data = indata.copy()
        curr_data = curr_data.astype(np.float64)

        # trigger has been tripped, simply record untill reach number of blocks
        if self.is_exceed:
            self._all_data.put(curr_data)
            if self._all_data.qsize() >= self.numblocks - 1:
                raise(sd.CallbackStop)
            return

        # special case for first sample
        if self._lastdata.empty():
            self._lastdata.put(curr_data)
            return

        # construct array of this sample and last
        full_data = np.concatenate([self._lastdata.get(), curr_data])
        self._lastdata.put(curr_data)

        # process last 2 samples
        data_FT = np.fft.fft(full_data[:, 0])
        self.is_exceed = np.any(np.abs(data_FT[self.fci])
                                 > self.record_threshold)
        self.last_center = self._fci_inverse[np.argmax(np.abs(data_FT[self.fci]))]

        if self.is_exceed:
            self._all_data.put(full_data)
