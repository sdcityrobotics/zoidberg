.. fish hawk documentation master file, created by
   sphinx-quickstart on Fri Nov 23 13:21:58 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to fish hawk's documentation!
=====================================
**Fish hawk** is a simple interface for working with the `pixhawk`_ auto-pilot
module. It is not designed to offer the full capability of `mavros`_, which is
used on the `SDCR`_ Zoidberg submarine robot. However, it does not require
`ROS`_, which has proven to be a difficult install.

The primary interface to the pixhawk is the python package `pymavlink`_, which
has python2 and provisional python3 support. This package seems to be the most
widely used python interface, though its it's documentation is spare at times.
Most of the code used in this package is found in a series of code snippits
written by `ardusub`_. As such, it may be specific to the ardusub firmware on
the pixhawk, but quite how is unclear.

.. _fish hawk: http://github.com/nedlrichards/fish_hawk
.. _SDCR: http://sdcityrobotics.org/
.. _pixhawk: http://pixhawk.org/
.. _ROS: http://www.ros.org/
.. _mavros: http://wiki.ros.org/mavros
.. _pymavlink: http://github.com/ArduPilot/pymavlink
.. _ardusub: http://www.ardusub.com/developers/pymavlink.html

Installation
------------
The primary interface is through the fish_hawk node, which is installed as a
python package. Since this package does not currently live on pypi, it is
necassary to first clone the source and install from the source folder itself.
This is done by first using git to clone the `fish hawk`_ source code.
This folder can be installed where ever is most convient for you. Then,
navigate to the new fish-hawk folder, it is important to be in the folder with
a setup.py file in it, and then type

.. code-block:: bash

    pip install .

This assumes that there is an active anaconda enviornment enabled. This command
should not require sudo. If it asks for a password, cancel and use

.. code-block:: bash

    pip install . --user

Optional installs
-----------------
There are currently two optional installs for this package

1. controller
2. zed

To install the controller package first follow the install instructions for
`cython-hidapi <https://github.com/trezor/cython-hidapi>`_.

To install the zed package first follow the install instructions for
`pyzed <https://github.com/stereolabs/zed-python>`_.

After completing the  the specific installations,  install an optional feature
with the following command, i.e. controller

.. code-block:: bash

    pip install .[controller]



Examples
--------

**Getting started**

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   index
   pixhawk
   controller
   examples
