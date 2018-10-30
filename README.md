# fish_hawk

Library designed to interface with a PIXHAWK autopilot module. This is split
into a few scripts, which exist in the upper folder, and a node, which is in
the inner fish_hawk folder. The node has to be installed, and this is done
by first navigating to the upper folder (with setup.py in it) and typing

```
pip install .
```

This assumes that there is an active anaconda enviornment enabled. This command
should not require sudo. If it asks for a password, cancel and use

```
pip install . --user
```
