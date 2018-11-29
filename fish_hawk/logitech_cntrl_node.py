from __future__ import division

import hid
from time import time
from fish_hawk import timestamp, pause

class ManualControlNode:
    """A class to allow for manual flight control of Zoidberg"""
    def __init__(self):
        """Basic info that specifies the logitech controller"""
        self.vendorID = 0x046D
        self.productID = 0xC216
        self.hiddevice = hid.device()
        self.numout = 8  # number of outputs from controller
        self._message = [128] * self.numout
        # motor out commands, each of the 4 DOF are from -100 to 100
        self.vel_forward = 0
        self.vel_side = 0
        self.vel_dive = 0
        self.vel_turn = 0

    def isactive(self, to_open):
        """Open and close communication"""
        if to_open:
            self.hiddevice.open(self.vendorID, self.productID)
            # enable non-blocking mode
            self.hiddevice.set_nonblocking(1)
        else:
            self.hiddevice.close()

    def check_readings(self):
        """return most recent readings mapped to motor commands"""
        # get the most recent reading
        isnew = self._read_buffer()
        if isnew:
            self.vel_side = (self._message[0] - 128) * 100 / 128
            self.vel_forward = -(self._message[1] - 128) * 100 / 128
            self.vel_turn = (self._message[2] - 128) * 100 / 128
            self.vel_dive = -(self._message[3] - 128) * 100 / 128

    def _read_buffer(self):
        """Get most current reading"""
        isnew = False # assume there won't be any messages
        # log comms untill a None is returned (exhausted buffer)
        d = self.hiddevice.read(self.numout)
        while d:
            isnew = True
            # save message as most recent
            self._message = d
            d = self.hiddevice.read(self.numout)
        return isnew

if __name__ == "__main__":
    update_period = 0.05
    cntr = ManualControl()
    try:
        print("starting up communication with logitech controller")
        cntr.isactive(True)
        while True:
            loop_start = time()
            cntr.check_readings()
            print("command out: fb %.2f, lf %.2f ud %.2f turn %.2f"%(
                cntr.vel_forward, cntr.vel_side, cntr.vel_dive, cntr.vel_turn))
            # sleep to maintain constant rate
            pause(loop_start, update_period)
    finally:
        print("Shutting down communication with logitech controller")
        cntr.isactive(False)
