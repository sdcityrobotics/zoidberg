Logitech Controller
===================

The logitech controller is used to move the robot around in manual control. It
uses `cython-hidapi`_ to interface with the controller.

Accessing the controller directly can raise issues with permissions. First, add
user to the ``plugdev`` group. You can see your current groups with the command

``groups``

*These next steps will probably require superuser privileges*

Add the current user (newuser in this example, change to match your username)
to the group plugdev

``usermod -a -G plugdev newuser``

Then, this `hidapi-udev`_ rule is added to the udev rules directory:

``/etc/udev/rules.d``

*Currently only tested on a Debian 9 system.*

The command ``udevadm control --reload-rules`` reloads the rules. The best way
to ensure the rule has been loaded is a restart.

.. _cython-hidapi: https://github.com/trezor/cython-hidapi
.. _hidapi-udev: http://github.com/nedlrichards/fish_hawk/tree/master/fish_hawk/udev/99-hidraw-permissions.rules
