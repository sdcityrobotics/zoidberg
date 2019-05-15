"""
==============
Acoustics node
==============
Communication node for beagle bone acoustics board. Data is transmitted from
the beagle bone over a tcp socket.
"""

import socket
import numpy as np
import threading
import queue

HOST = 'localhost'
PORT = 50007
all_data = queue.Queue()

def beagle_server(host):
    """Open up a server than listend to the beagle whenever it has data"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        dout = []
        with conn:
            while True:
                data = conn.recv(1024)
                if not data: break
                dout.append(data)
            # convert from bytes back to a numpy array
            p_atfc = np.frombuffer(b''.join(dout), dtype=np.complex64)
            p_atfc = p_atfc.reshape(-1, 3)
            all_data.put(p_atfc)

def start_socket(stop, host):
    """maintain a server, but let it check periodicly if it should shutdown"""
    while not stop():
        try:
            beagle_server(host)
        except socket.timeout:
            # this is expected behavior, used to check periodicly if we should
            # shut down communication with beagle bone
            pass

class AcousticsNode:
    """Comms node to beagle bone"""
    def __init__(self, tcp_host, filepath=None):
        """Start up socket communcation with beagle bone"""
        self.host = tcp_host
        self.filepath = filepath
        # most current reading
        self.curr_read = None
        # used when opening a log file
        self.all_read = None
        self.curr_index = 0
        self.read_step = 20  # sort of made up, readings per check

        # recording specifications
        self.datatype = np.complex64  # data type of each reading
        self.num_channels = 3  # number of acoustics channels

    def isactive(self, to_stream):
        """startup/shutdown communciations with beagle bone"""
        # don't do anything if we are just reading from a log file
        if self.filepath is None:
            return

        # open up a TCP server for comms with Beaglebone
        if to_stream:
            stop_threads = False
            # startup tcp server in its own thread
            t1 = threading.Thread(target=start_socket,
                                  args=(lambda: stop_threads, self.host,))
            t1.start()
        else:
            # this shuts down server
            stop_threads = True

    def check_readings(self):
        """Read most current data from buffer"""
        # loading data from log file
        if self.filepath is not None:
            if self.all_read is None:
                return False
            else:
                ei = self.curr_indexi + self.read_step
                if ei >= self.all_read.shape[0]:
                    return False
                self.curr_read = self.all_read[self.curr_index: ei, :]
                self.curr_index = ei
                return True

        # stream of data from beaglebone
        # check that there is new data avalible
        isnew = not all_data.empty()

        if isnew:
            # read most current data
            qsize = all_data.qsize()
            curr_read = [all_data.get_nowait() for _ in range(qsize)]
            self.curr_read = np.concatenate(curr_read)

        return isnew

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
