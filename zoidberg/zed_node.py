"""
Zed Camera
==========
Standard interface between Zoidberg and zed camera.
"""
import pyzed.sl as sl
from zoidberg import timestamp
import PIL as pl

class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self):
        """Basic initilization of camera"""
        self.init = sl.InitParameters()
        self.cam = sl.Camera()
        self.zed_param = None
        self.zedStatus = None
        self.runtime_param = None
        self._image = sl.Mat()
        self._depth = sl.Mat()
        self.image = None
        self.depth = None
        self.image_time = None
        
    def isactive(self, is_on):
        """Turn communication with the zed camera on and off"""
        if self.cam.is_opened() != is_on:
            self.zedStatus = self.cam.open(self.init)
            if self.zedStatus != sl.ERROR_CODE.SUCCESS:
                print(repr(self.zedStatus))
                self.zedStatus = self.cam.close()
                raise SystemExit
            else:
                self.runtime_param = sl.RuntimeParameters()
        else:
            self.zedStatus = self.cam.close()
            print(self.zedStatus)

    def check_readings(self):
        """Take a picture if avalible"""
        status = self.cam.grab(self.runtime_param) #run camera
        if status == sl.ERROR_CODE.SUCCESS:
            isnew = True
            self.image_time = timestamp()
            self.cam.retrieve_image(self._image, sl.PyVIEW.PyVIEW_LEFT)
            self.cam.retrieve_measure(self._depth, sl.PyMEASURE.PyMEASURE_DEPTH)
            self.image = self._image.get_data()
            self.depth = self._depth.get_data()
        else:
            isnew = False
        return isnew

    def save_image(self, save_folder):
        """Save current image to file"""
        pass

    def print_camera_information(self):
        """Print out some pertinent information"""
        print("Current Zed camera information:")
        print("Resolution: {0}, {1}.".format(round(self.cam.get_resolution().width, 2), self.cam.get_resolution().height))
        print("Camera FPS: {0}.".format(self.cam.get_camera_fps()))
