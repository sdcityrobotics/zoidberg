# fish_hawk

Library designed to interface with a PIXHAWK autopilot module.
The code should be run in python2. I prefer running the code in ipython2, and
editing the source in a good text editor (not to get specific :). Basicly,
auto indent with spaces for tabs is really a must.

# TODO
The next step is to work with waypoint files. There is fairly good discription
of the low level message passing for this on

http://qgroundcontrol.org/mavlink/waypoint_protocol

but this is very light on the implimentation.

The basic program will basicly be to:

1) takeoff to altitude (Hopefully this works for dives)

2) turn to heading

3) set throttle

4) run for a set amount of time

5) turn off throttle

6) idle at waypoint

We'll see how that goes...
