import math
from pymavlink import mavutil

class Helmsman:
    """Generates RC messages for basic navigation"""
    def __init__(self):
        pass

    def change_depth(self, desired_depth, is_blocking):
        """move robot to another depth"""
        pass

    def change_heading(self, desired_heading, is_blocking):
        """Change robot heading"""
        pass

    def to_waypoint(self, desired_position, is_blocking):
        """Move robot to desired waypoint. First turn, then straight"""
        pass

    def throtle(self, velocity, timeout, is_blocking):
        """Move forward at a constant velocity for a set period of time"""
        pass
