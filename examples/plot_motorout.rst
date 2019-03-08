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

.. code:: python
    from time import time
    import numpy as np
    import matplotlib.pyplot as plt
    from serial import SerialException
    from fish_hawk import PixhawkNode, pause

    update_period = 0.05
    # Mac OSX address
    #device = '/dev/tty.usbmodem1'
    # Linux address
    device = '/dev/ttyACM0'

    pn = PixhawkNode(device)

    # try loop is used to ensure that communication with pixhawk is
    # terminated.
    try:
        # startup data stream
        pn.isactive(True)
        # change to stablize mode
        pn.change_mode('STABILIZE')
        motor_out = []
        readtime = []

        total_time = 3  # total collection time, seconds
        run_start = time()
        loop_start = run_start

        while run_start + total_time > loop_start:
            loop_start = time()
            pn.check_readings()
            if pn.timestamp == 0 or pn.rc_out[0] == 0:
                continue
            motor_out.append(np.array(pn.rc_out[:6]))
            readtime.append(pn.timestamp / 1000)
            # sleep to maintain constant rate
            pause(loop_start, update_period)
    except SerialException:
        print('Pixhawk is not connected to %s'%device)
        raise
    finally:
        print('Shutting down communication')
        pn.isactive(False)

    motor_out = np.array(motor_out)
    readtime = np.array(readtime)

    fig, axes = plt.subplots(2, 1, sharex=True)
    chan_odd = axes[0].plot(readtime - readtime[0], motor_out[:, [0, 2, 4]])
    chan_even = axes[1].plot(readtime - readtime[0], motor_out[:, [1, 3, 5]])

    axes[1].set_xlabel('time, s')
    axes[0].set_title('Percent motor command')
    axes[0].legend(chan_odd, ['chan 1', 'chan 3', 'chan 5'])
    axes[1].legend(chan_even, ['chan 2', 'chan 4', 'chan 6'])
