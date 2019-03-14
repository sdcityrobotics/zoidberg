.. _plot motor out:

Ploting motor outputs from pixhawk for stablize mode
====================================================

Depth Hold mode is used by default for the Zoidberg robot. To paraphase the
ardusub documentation "Depth hold mode passes the pilot inputs directly to the
motors, with heading and attitude and depth stabilization." To parse this out,
the sub will respond to RC commands as usual for manual mode, but will
work to hold its heading and depth. Additionally, it will work to hold itself
flat (no roll and pitch), but it needs to be fully actuated to do this
completely (a 6 degree of freedom motor setup).

The challenge for working with Depth hold mode is that the Pixhawk needs the
motors to be installed in the correct direction. Motor direction can be
controlled using the `QGroundControl`_ GUI, but it is helpful to visualize the
current motor responeses to pixhawk motion to get a feel for which motors might
need direction swapping.

.. _QGroundControl: http://qgroundcontrol.com/

.. literalinclude:: ../../zoidberg_cc/plot_motorout.py
