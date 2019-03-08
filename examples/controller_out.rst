.. _controller out:

Printing controller output
==========================

Simply print the output from logitech controller to the screen. This is useful
if only to verify that it is working at all.

.. code:: python

    from fish_hawk import ManualControlNode, pause
    from time import time

    update_period = 0.05
    cntr = ManualControlNode()
    try:
        print("starting up communication with logitech controller")
        cntr.isactive(True)
        while True:
            loop_start = time()
            cntr.check_readings()
            print("command out: fb %.2f, lf %.2f ud %.2f turn %.2f"%(
                cntr.vel_forward, cntr.vel_side, cntr.vel_dive, cntr.vel_turn))
            # sleep to maintain constant rate
            pause(loop_start, update_period)
    finally:
        print("Shutting down communication with logitech controller")
        cntr.isactive(False)
