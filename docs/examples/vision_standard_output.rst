.. _object detection output:

Standard output string for an object dection
=============================================
Vision will return this standard string for each object identified in an image.
The sting will look like

``img_19_067_11_50_05_560, 001, 463, 0432, 034, 056, 19_067_11_50_05_561``

The first field is the image name, which is mostly a timestamp. The second
field is the id value of the object. The third to sixth string describe the
pixels of the detction. The last field is the time stamp at the end of the
image processing.

.. literalinclude:: _code/vision_standard_output.py
