import numpy as np
import matplotlib.pyplot as plt
from math import pi
import scipy.signal as sig
from scipy.io import wavfile

class NarrowBand:
    """A narrow banded pulse"""
    def __init__(self, fc, bw, fs):
        """Duty cycle is length pulse is active"""
        self.period = 1 / bw  # basic fourier transform uncertainty
        num_samples = int(np.ceil(self.period * fs))
        # make even
        if num_samples % 2:
            num_samples += 1
        self.num_samples = num_samples
        self.time = np.arange(num_samples) / fs
        self.fc = fc
        self.bw = bw
        self.fs = fs
        self.signal = self.narrow_band()

    def narrow_band(self):
        """create an narrow banded pulse to specs"""
        xmitt = np.sin(2 * pi * self.fc * self.time)
        # window is unknown, assuming a pretty narrow mainlobe
        window = sig.kaiser(self.time.size, 1.0 * pi)
        xmitt *= window
        return xmitt

    def FT(self):
        """Compute the signal's FT"""
        NFFT = int(2 ** np.log2(np.ceil(self.signal.size) + 1))
        FT = np.fft.rfft(self.signal, NFFT)
        f = np.arange(NFFT / 2) / NFFT * self.fs
        return (FT, f)

if __name__ == "__main__":
    fc = 5000  # Hz
    bw = 500  # Hz
    fs = 96e3  # Hz
    lfm = NarrowBand(fc, bw, fs)
    FT, freq = lfm.FT()

    fig, ax = plt.subplots()
    ax.plot(lfm.time * 1e3, lfm.signal)
    ax.set_xlabel('time, ms')
    ax.set_ylabel('amplitude')
    ax.set_title('probe signal time series')

    fig, ax = plt.subplots()
    db_FT = 20 * np.log10(np.abs(FT))
    db_FT -= np.max(db_FT)
    ax.plot(freq / 1e3, db_FT)
    ax.set_xlabel('frequency, kHz')
    ax.set_ylabel('Magnitude, dB')
    ax.set_title('probe signal fourier transform')

    plt.show(block=False)
