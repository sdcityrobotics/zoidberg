# zoidberg_ros
navigation for zoidberg

Install
-------

This package is installed using catkin_make. Place zoidberg_ros folder into

    catkin_workspace/src/

directory (fill in catkin_workspace with your specific catkin workspace
directory). The basic instructions for making the workspace are found in the
[Ros tutorial][RosT1]. Permanently source your local catkin workspace in the home .bashrc file. For instance, if you are in you catkin_workspace home folder,
```
cd devel
pwd
```
copy the pwd output, and type
```
echo "source <pwd output>/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Once the zoiderg_nav package is in place, move to the base catkin_workspace
and run catkin_make

```
cd catkin_workspace
catkin_make
```

Once installed, this package defines a number of ROS messages related to
 navigation and a few ROS nodes. A launch file is used to set up navigation.

```
roslaunch zoidberg_ros zoidberg_ros.launch
```

Ubuntu sets permisions for using serial ports, and if you get an error which ends in Permission Denied, it is probably fixed by adding yourself to the group dialout. 
```
sudo usermod -a -G dialout <username>
```
Username is found by clicking on the gear on the top right of the Ubuntu screen. A restart may be needed after this command to have the changes take effect.

[RosT1]: http://wiki.ros.org/ROS/Tutorials/InstallingandConfiguringROSEnvironment
