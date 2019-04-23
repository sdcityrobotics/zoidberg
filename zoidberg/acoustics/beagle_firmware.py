"""
=============================
Beagle bone acoustic recorder
=============================
This code is meant to run without interruption on the beagle bone black. It
assumes a there is a bela CTAG cape attached.
"""
import numpy as np
from math import pi

fs = 96000  # this should be higher than 80000, and a multiple of 1000
buffer_length = 2 ** 8  # number of samples to process at once from CTAG
num_channels = 3  # number of hydrophone channels

# window specification, this is taken from:
# Heinzel G. et al., “Spectrum and spectral density estimation by the Discrete
# Fourier transform (DFT), including a comprehensive list of window functions
# and some new flat-top windows”

winwidth = int(fs / 1e3)  # 1 ms window
overlap = .598  # a value between 0 and 1, Heinzel's optimal overlap


# sampling positions along a continous stream of data
num_overlap = int(np.ceil(winwidth * overlap))  # overlap as an integer


class NarrowBandDigitizer:
    """
    Digitize hydrophone data as a stream of complex amplitudes taken at the
    center frequency of interest
    """

    def __init__(self, fc):
        """initilize data stream variables"""
        self.fc = fc
        # edge case tracking
        self.tail_data = np.zeros((0, num_channels))

        # precompute window, this math saves an import of scipy :)
        nuttall3b = [.4243801, .4973406, .0782793]
        fac = np.linspace(-np.pi, np.pi, winwidth)
        self.window = np.zeros(winwidth)
        for k in range(len(nuttall3b)):
            self.window += nuttall3b[k] * np.cos(k * fac)

        # number of samples to move each calculation
        self.num_step = winwidth - num_overlap

        # precompute twidle factors
        # https://forum.bela.io/d/799-high-frequency-narrow-banded-beamforming
        self.twidle = np.exp(1j * 2 * pi * fc / fs * np.arange(winwidth))
        self.twidle *= self.window

    def process(self, recorded_data):
        """
        Compute single frequency samples from a recorded time series
        """
        # add old data to start before processing
        all_data = np.concatenate([self.tail_data, recorded_data])

        # compute where the windows are going to be
        num_windows = int(np.floor((all_data.shape[0] - winwidth) /
                          self.num_step))
        win_position = np.arange(num_windows) * self.num_step

        # deal with the end case. There will always be some lost data
        # at the edges, so we need to save it for the next processing cycle
        tail_start = win_position[-1] + self.num_step
        self.tail_data = np.copy(all_data[tail_start: , :])

        # Calculate measurements
        p_atfc = []
        for wp in win_position:
            # matrix multiply data to get DFT result at a single frequency
            p_FT = self.twidle @ all_data[wp: wp + winwidth, :]
            p_atfc.append(p_FT)

        return np.array(p_atfc)

