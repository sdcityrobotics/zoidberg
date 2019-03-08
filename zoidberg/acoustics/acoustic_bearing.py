import numpy as np
from math import pi
from scipy.signal import firwin, convolve, resample
from scipy.interpolate import interp1d

class BearingBeamform:
    """beamforming processing"""
    def __init__(self, fc, bw, fs, sample_length, channel_delays):
        """Baseband and time domain beamform input data"""
        self.fc = fc
        self.fs = fs
        self.bw = bw
        self.channel_delays = np.array(channel_delays, ndmin=1)
        self.sample_length = sample_length

        # baseband information
        self.f_bb = 1 * self.bw
        self.fcut = 3 * self.bw
        self.numtaps = 1024
        # find nearest decimation for basebander
        self.decimation = int(np.ceil(self.fs / self.fcut))
        # private time axis is not decimated
        self._taxis = None
        # public time axis has been decimated (downsampled)
        self.taxis = None

    def baseband(self, data_in, center_freq, is_inverse=False):
        """baseband data"""
        sample_length = data_in.shape[-1]
        # private time axis is not decimated
        self._taxis = np.arange(1. * sample_length) / self.fs
        # public time axis has been decimated (downsampled)
        self.taxis = (self._taxis[self.numtaps // 2: ]).copy()
        self.taxis = self.taxis[: : self.decimation]
        self.taxis -= self.taxis[0]
        # setup band pass filter
        edges = [center_freq - 1.5 * self.bw, center_freq + 1.5 * self.bw]
        bp_filt = firwin(self.numtaps, edges, window='blackmanharris',
                         pass_zero=False, fs=self.fs)
        # represent filter in the frequency domain
        bp_FT = np.fft.fft(bp_filt, n=sample_length)
        # add a hilbert transform to bandpass filter
        bp_FT[1 : sample_length // 2] *= 2
        bp_FT[sample_length // 2: ] *= 0

        fbb = center_freq - self.f_bb
        in_data_FT = np.fft.fft(data_in, axis=-1)
        in_data_FT *= bp_FT[None, :]
        phase_bb = np.exp(-2j * pi * fbb * self._taxis)[None, :]
        recorded_data_bb = np.fft.ifft(in_data_FT, axis=-1)
        recorded_data_bb *= phase_bb
        # shift for convolution length
        recorded_data_bb = recorded_data_bb[:, self.numtaps // 2: ]
        # decimate recorded time series
        recorded_data_bb = recorded_data_bb[:, : : self.decimation]
        return recorded_data_bb

        if is_inverse:
            # remove hilbert transform of data
            in_data_FT[1:self.NFFT // 2] /= 2
            # make data conjugate symetric
            in_data_FT[self.NFFT // 2: ] = \
                np.conj(in_data_FT[self.NFFT // 2])[::-1]

        if is_inverse:
            phase_bb = np.conj(phase_bb)

        in_data_FT = np.fft.fft(data_in * phase_bb, axis=-1)

    def beamform(self, baseband_data, center_freq, relative_delays, iscoherent=False):
        """Construct a time domain interpolator for data, delay and sum"""
        upsample = 5
        # upsample signal by adding zeros to higher frequency sampling
        bb_FD = np.fft.fft(signal_bb, axis=-1)
        bb_up_FD = np.zeros((num_channels, bb_FD.shape[-1] * upsample),
                            dtype=np.complex_)
        bb_up_FD[:, :bb_FD.shape[-1]] = bb_FD
        # construct upsampled time axis
        DT = (self.taxis[-1] - self.taxis[0]) / (self.taxis.size - 1)
        f_up = np.arange(bb_up_FD.shape[-1]) / bb_up_FD.shape[-1]
        f_up /= DT
        f_up *= upsample
        # construct unshifted reference channel
        ref_chan = np.fft.ifft(bb_up_FD[0, :])
        ref_chan *= upsample
        # create shifted versions of second channel
        shift_phase = np.exp(2j * pi * f_up * relative_delays[:, None])
        shift_phase *= np.exp(2j * pi * (center_freq - self.f_bb) * relative_delays[:, None])
        shift_chan = bb_up_FD[1, :] * shift_phase
        shift_chan = np.fft.ifft(shift_chan, axis=-1)
        shift_chan *= upsample
        if iscoherent:
            beam_out = shift_chan + ref_chan
        else:
            beam_out = np.abs(shift_chan) + np.abs(ref_chan)
        return beam_out


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from probe_signal import NarrowBand

    fc = 5000  # Hz
    bw = 500  # Hz
    fs = 96e3  # Hz
    num_channels = 2
    signal_bearing = -pi / 4
    lfm = NarrowBand(fc, bw, fs)

    # plane wave delay model
    c = 1500.        # sound speed in water, m/s
    d = 0.5          # distance between 2 elements, meters
    num_looks = 300  # number of look directions

    # construct search axis from left to right, radians
    look_axis = np.arange(num_looks) / num_looks * pi - pi / 2
    # plane wave channel delays, seconds
    delays = np.sin(look_axis) * d / c

    # create a test vector
    num_samples = 2 ** 14
    tshift = np.sin(signal_bearing) * d / c
    ishift = int(np.round(tshift * fs))
    sig_in = np.zeros((num_channels, num_samples), dtype=np.float64)

    istart = 2 ** 12

    sig_in[0, istart: istart + lfm.num_samples] = lfm.signal
    sig_in[1, istart + ishift: istart + lfm.num_samples + ishift] = lfm.signal

    beamer = BearingBeamform(fc, bw, fs, num_samples, delays)

    signal_bb = beamer.baseband(sig_in, fc)
    dt = (beamer.taxis[-1] - beamer.taxis[0]) / (beamer.taxis.size - 1)

    beam_out = beamer.beamform(signal_bb, fc, delays)
    beam_out_coh = beamer.beamform(signal_bb, fc, delays, iscoherent=True)

    b_max = np.sum(np.abs(beam_out) ** 2, axis=-1)
    b_max_coh = np.sum(np.abs(beam_out_coh) ** 2, axis=-1)
    bi = np.argmax(b_max)
    maxi = np.argmin(np.abs(look_axis - signal_bearing))

    fig, ax = plt.subplots()
    ax.plot(look_axis, b_max)
    ax.plot(look_axis, b_max_coh)
    ax.plot(look_axis[maxi], b_max[maxi], '*')

    plt.show(block=False)
