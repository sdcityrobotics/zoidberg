.. _Mission multiprocessing:

Mission and multiprocessing
===========================

Mission is responsible for spreading the robotic processing out over a the four
cores of the Nvidia `TX1`_. This section is Unix only!


.. literalinclude:: _code/parent_pipe.py

.. literalinclude:: _code/child_pipe.py


.. _TX1: http://www.nvidia.com/en-us/autonomous-machines/embedded-systems-dev-kits-modules/
