"""
Mission node
============
THIS CODE IS COMPLETELY UNTESTED AND IS MEANT AS A TEMPLATE ONLY

Provides a framwork to build basic behaviors used to make up a mission.
"""
import roslib
import rospy
import time
import zoidberg_ros.msg
from mavros_msgs.srv import StreamRate, CommandBool, SetMode

class Mission:
    """Build up a mission with common task framework"""
    def __init__(self):
        """Setup possible tasks"""
        self.rate = rospy.Rate(10)
        self.curr_state = None
        self.curr_vision = None
        self.desired_state = None
        # All the inputs that come out of ROS land
        rospy.Subscriber("/navigation",
                         zoidberg_ros.msg.State,
                         self._set_curr_navigation)
        rospy.Subscriber("/vision",
                         zoidberg_ros.msg.Vision,
                         self._set_curr_Vision)

    def do(self, desired_state, isterm_cb, timeout, guidance_cb=None):
        """callbacks provide termination condition and can modify guidance"""
        tstart = time.time()
        while not isterm_cb(self.curr_state, self.curr_vision):
            # timeout termination behvior
            if time.time() - tstart > timout:
                rospy.loginfo('Timeout preempted')
                break
            if guidance_cb is not None:
                # guidance callback is allowed to make small changes to the
                # guidance specified by the mission script
                delta_guidance = guidance_cb(self.curr_state, self.curr_vision)
            else:
                # if guidance callback is not defined, delta is set to 0
                # Ros messages initialize to 0 by default
                delta_guidance = zoidberg_ros.msg.VehicleState()
            # TODO: Limit delta values from callback
            target_depth = desired_state.depth\
                           + delta_guidance.depth
            target_heading = desired_state.heading\
                             + delta_guidance.heading
            target_vx = desired_state.vx + delta_guidance.vx
            target_vy = desired_state.vy + delta_guidance.vy
            guideout = zoidberg_ros.msg.State(depth=target_depth,
                                              heading=target_heading,
                                              vx=target_vx,
                                              vy=target_vy)
            # log guidance message and publish it
            rospy.loginfo(guideout)
            self.guidancep.publish(guideout)
            # rest
            self.rate.sleep()

    def _set_curr_vision(self, curr_vision):
        """Set object x and y coordinates published from vision"""
        self.curr_vision = curr_vision

    def _set_curr_state(self, curr_state):
        """Set the current state published from navigation"""
        self.curr_state = curr_state
