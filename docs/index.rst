.. fish hawk documentation master file, created by
   sphinx-quickstart on Fri Nov 23 13:21:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Zoidbergs's documentation!
=====================================
**Zoidberg** is a simple interface for working with the `pixhawk`_ auto-pilot
module. It is not designed to offer the full capability of `mavros`_, however,
it does not require `ROS`_, which has proven to be a difficult install.

The primary interface to the pixhawk is the python package `pymavlink`_, which
has python2 and provisional python3 support. This package seems to be the most
widely used python MAV interface, though it's documentation is spare at times.
Most of the code used in this package is found in a series of code snippits
written by `ardusub`_. As such, it may be specific to the ardusub firmware on
the pixhawk, but quite how is unclear.

.. _SDCR: http://sdcityrobotics.org/
.. _pixhawk: http://pixhawk.org/
.. _ROS: http://www.ros.org/
.. _mavros: http://wiki.ros.org/mavros
.. _pymavlink: http://github.com/ArduPilot/pymavlink
.. _ardusub: http://www.ardusub.com/developers/pymavlink.html

Sections
--------

**Instrument I/O**

.. toctree::
   :maxdepth: 1
   :caption: Instruments:

   pixhawk <pixhawk>

**General discussion**

.. toctree::
   :maxdepth: 1
   :caption: Discussion:

   examples
   standards
   strategy <strategy>
