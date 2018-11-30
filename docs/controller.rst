Logitech Controller
===================

The logitech controller is used to move the robot around in manual control. It
uses `cython-hidapi`_ to interface with the controller.

Accessing the controller directly can raise issues with permissions. This is
currently only tested on a Debian 9 system. This `hidapi-udev`_ rule is added
to the udev rules directory: /etc/udev/rules.d

The command ``udevadm control --reload-rules`` reloads the rules.

.. _cython-hidapi: https://github.com/trezor/cython-hidapi
.. _hidapi-udev: https://github.com/nedlrichards/fish_hawk/fish_hawk/udev/99-hidraw-permissions.rules
