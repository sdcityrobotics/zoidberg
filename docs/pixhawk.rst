Pixhawk Autopilot module
========================

The `pixhawk`_ autopilot module is used to abstract away motion control of
Zoidberg.

Accessing the pixhawk directly can raise issues with permissions. This is best
adressed by adding your user to the ``dialout`` group. You can see your current
groups with the command

``groups``

*These next steps will probably require superuser privileges*

Add the current user (newuser in this example, change to match your username)
to the group dialout

``usermod -a -G dialout newuser``

A restart may be necassary for changes to take effect.

.. _pixhawk: http://pixhawk.org/
