# Zoidberg

This package is designed to work with python3. As all of the packages are in
python, this is expected to work on all 3 major OS: Linux, MacOS and Windows.
That being said, this documentation is heavily skewed to Linux specific
instructions.

It is a really good idea to work with a user installed python3 program, and not
to rely on the system python3. A very simple way to do this, common in
scientific computing, is to use [Anaconda](https://conda.io/miniconda.html).
This installation will create a seperate python program on your computer which
is run by the user instead of the system default. In this way the system is
happy (it gets an older, stable version), and the user is happy (with a newer,
more activly developed version).

The anaconda distribution framework is also great for installing complicated
packages like opencv. Most common packages are installed using the command line
tool conda. If you have conda, go ahead and run the line:

    conda install numpy scipy pyserial matplotlib setuptools ipython

There is another package manager which does basicly the same thing, pip.
When the conda installer can't find a package, or if you can not install
Anaconda, pip is the next best thing. Under no circumstances should you belive
anyone who tells you to use the package manager easy_install.

If you are using system python3, it is important to install pip3. Really, this
is a painful thing to do, and probably only be necassary for the computer
on-board the robot, which is esentially a souped up microprocessor.

## Installation

Since this package does not currently live on pypi, it is
necassary to first clone the source and install from the source folder itself.
This is done by first using git to clone the source code. Next, navigate to the
zoidberg folder on your own computer (this folder has a setup.py file in it),
then type

    pip install .

This assumes that there is an active anaconda enviornment enabled. This command
should not require sudo. If it asks for a password, cancel and use

    pip install . --user

## Device specific installs

There are currently two devices supported by this package

1. pixhawk
2. zed camera

### Pixhawk

The pixhawk requires the package [pymavlink](https://github.com/ArduPilot/pymavlink).
This is installed by default because it is straight forward with pip.

### Zed camera

1. To install the zed package first follow the install instructions for
[pyzed](https://github.com/stereolabs/zed-python).

2. Install opencv. This is simple with conda

    conda install opencv

If conda is not available,
[Manuel Ignacio Lopez Quintero](http://milq.github.io/install-opencv-ubuntu-debian/)
has detailed instructions on alternative install methods.

## Documentation

The documentation is hosted on ReadTheDocs at https://zoidberg-sdcr.readthedocs.io/en/latest/
