"""
Class to store pixhawk readings
"""
class PixhawkReading():
    """Define pixhawk information of interest"""
    def __init__(self):
        self.timestamp = 0
        self.heading = 0.0
        self.rc_command = [ 0.0 for dim0 in range(4) ]
        self.rc_out = [ 0.0 for dim0 in range(8) ]
        self.mode = ''
