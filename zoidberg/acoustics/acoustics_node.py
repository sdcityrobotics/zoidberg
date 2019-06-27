"""
==============
Acoustics node
==============
Communciation between TX1 and the beaglebone soundcard. Once data is on-board
the TX1, detect pings with a threshold, then determine arrival time and angle.

Requires a compiled version of audio_data_t. This is done at the command line.
First, navigate to the aoustics/ folder
lcm-gen -p audio_data_t.lcm
"""
import numpy as np
from math import pi
import threading
import select

import lcm
from zoidberg import empty_value
from zoidberg_lcm import audio_data_t

fs = 96000  # sampling frequency
num_channels = 3

class AcousticsNode:
    """Download sound information from beaglebone, beamform at each ping"""
    def __init__(self, fc):
        """This node requires an external source of acoustic data"""
        # center frequency that we are looking for
        self.fc = fc

        # This information is designed to be used by zoidberg mission
        self.arrival_time = empty_value
        self.bearing = empty_value

        # This information is downloaded from beagle bone
        # sampling frequency
        self.fs = fs
        # time at which data was received
        self.timestamp = None
        # latest data
        self.recorded_data = None
        # numer of raw samples in each reading
        self.num_step = None

        # ping detection information
        self.dx = 0.0185  # spacing of hydrophones, (m)
        self.c = 1480  # speed of sound, fresh water
        self.threshold = 1  # detection threshold
        self.dead_time = 0.2  # minimum time between detections, (s)
        self.num_snapshots = 4  # number of snapshots used in beamforming, > 1
        num_look = 300  # oversample in possible look directions
        # look directions are from -pi / 2 to pi / 2
        self.look_directions = np.arange(num_look) * pi / num_look - pi / 2
        k_x = (2 * pi * self.fc / self.c) * np.sin(self.look_directions)
        self.look_vectors = np.exp(1j * np.arange(num_channels)[:, None]
                                   * self.dx * k_x)

        # local variables for communication over lcm
        self.lc = None
        self.stop_threads = False

    def is_active(self, to_arm):
        """Startup and shut down communication with beagle over lcm"""
        if to_arm:
            # startup LCM communication
            self.lc = lcm.LCM()
            # subscribe LCM listener
            self.lc.subscribe("ACOUSTICS", self._get_handler())
            # Run listen loop in its own thread.
            t1 = threading.Thread(target=self._get_listener())
            # flag used to indicate that the thread should stop.
            self.stop_threads = False
            t1.start()
        else:
            self.stop_threads = True

    def process_data(self):
        """Detect pings, and beamform if present
        """
        # Threshold step, performed on first axis
        max_i = np.argmax(np.abs(self.recorded_data[0, :]))
        max_val = np.abs(self.recorded_data[0, max_i])

        # if we don't meet threshold requirement, return without do anything
        if max_val < self.threshold:
            return

        # estimate when the pressure exceeded the threshold
        is_over = np.abs(self.recorded_data[0, : max_i + 1]) > self.threshold
        fei = np.argmax(is_over)
        # compute arrival time in ms from midnight
        arrival_time = self.timestamp.split('_')
        arrival_time = float(arrival_time[-4]) * 3600 \
                     + float(arrival_time[-3]) * 60 \
                     + float(arrival_time[-2]) \
                     + float(arrival_time[-1]) / 1000
        arrival_time += fei * self.num_step / self.fs

        # check if we have sufficent dead time from last detection
        if self.arrival_time is not None \
            and arrival_time - self.arrival_time < self.dead_time:
            return

        # very sloppy check for edge case. just drop it if it comes up
        if (fei + self.num_snapshots) >= self.recorded_data.shape[1]:
            return

        # confirmed arrival, compute and log result
        self.arrival_time = arrival_time

        # beamform arrivals
        beams = self.recorded_data[:, fei: fei + self.num_snapshots]
        K = np.conj(beams) @ beams.T / self.num_snapshots
        B = (np.conj(self.look_vectors).T @ K) * self.look_vectors.T
        B = B.sum(axis=1)
        max_beam = np.argmax(B)
        self.bearing = self.look_directions[max_beam]

    def _get_listener(self):
        """return a function that starts an infinite loop in a seperate thread
        function stop() ends thread cleanly
        """
        tout = 0.1  # a timeout to force to check if thread has stopped
        def main_loop():
            """Function to allow self to be used between threads"""
            while not self.stop_threads:
                # select statement forces restart every timeout period
                rfds, wfds, efds = select.select([self.lc.fileno()],
                                                 [],
                                                 [],
                                                 tout)
                if rfds:
                    # call the handler if a message was published
                    self.lc.handle()
        return main_loop

    def _get_handler(self):
        """return a handler that records the latest message"""
        def lcm_handler(channel, data):
            """Function to allow self to be used between threads"""
            msg = audio_data_t.decode(data)
            self.timestamp = msg.timestamp
            self.num_step = msg.num_step
            self.fs = msg.fs
            # construct complex array from real and imaginary components
            self.recorded_data = np.array(msg.re_samples) \
                               + 1j * np.array(msg.im_samples)
            #self.recorded_data = np.transpose(self.recorded_data)
            # process new data
            self.process_data()
        return lcm_handler
