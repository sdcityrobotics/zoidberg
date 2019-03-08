.. _manual control:

Control motor outputs with logitech controller
==============================================

A simple pipe from the logitech controller to the pixhawk apm.


.. code:: python

    from fish_hawk import ManualControlNode, PixhawkNode, pause
    from serial import SerialException
    from time import time

    update_period = 0.05

    cntr = ManualControlNode()

    # Mac OSX address of pixhawk
    device = '/dev/tty.usbmodem1'
    pn = PixhawkNode(device)

    try:
        print("starting up communication with logitech controller")
        cntr.isactive(True)
        print("starting up communication with pixhawk")
        pn.isactive(True)
        while True:
            loop_start = time()
            cntr.check_readings()
            pn.check_readings()

            pn.send_rc(vel_forward=cntr.vel_forward,
                    vel_side=cntr.vel_side,
                    vel_dive=cntr.vel_dive,
                    vel_turn=cntr.vel_turn)

            print("servo out: {:d}  {:d}  {:d}  {:d}  {:d}  {:d}".format(
                *pn.rc_out[:6].astype(np.int_)))

            # sleep to maintain constant rate
            pause(loop_start, update_period)
    except SerialException:
        print('Pixhawk is not connected to %s'%device)
    finally:
        print("Shutting down communication with logitech controller")
        cntr.isactive(False)
        print('Shutting down communication with Pixhawk')
        pn.isactive(False)
