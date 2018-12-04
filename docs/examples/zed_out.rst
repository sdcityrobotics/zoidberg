.. _controller out:

Displaying zed camera output
============================

Display zed camera image (from left camera) and depth map in real time.

.. code:: python

    from fish_hawk import ZedNode, pause
    from time import time

    update_period = 0.05
    runzed = ZedNode()
    try:
        print("starting up communication with Zed camera")
        runzed.isactive(True)
        runzed.print_camera_information()
        while True: #waiting for 'q'
            loop_start = time()
            isnew = runzed.check_readings()
            if isnew:
                cv2.imshow("image", runzed.image)
                cv2.imshow("depth", runzed.depth)
            # sleep to maintain constant rate
            pause(loop_start, update_period)
    finally:
        print("Shutting down communication with Zed camera")
        cv2.destroyAllWindows()
        runzed.isactive(False)
