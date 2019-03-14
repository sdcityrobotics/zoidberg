"""
Zed Camera
==========
Standard interface between Zoidberg and zed camera.
"""
import pyzed.sl as sl
from zoidberg import timestamp
import PIL as pl

param = dict(camera_resolution=sl.RESOLUTION.RESOLUTION_HD720,
             depth_mode=sl.DEPTH_MODE.DEPTH_MODE_MEDIUM,
             coordinate_units=sl.UNIT.UNIT_METER,
             coordinate_system=sl.COORDINATE_SYSTEM.COORDINATE_SYSTEM_RIGHT_HANDED_Z_UP_X_FWD,
             camera_fps=10,
             camera_buffer_count_linux=1
        )


class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self):
        """Basic initilization of camera"""
        self.init = sl.InitParameters(**param)
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
        if is_on and not self.cam.is_opened():
            self.zedStatus = self.cam.open(self.init)
            if self.zedStatus != sl.ERROR_CODE.SUCCESS:
                print(repr(self.zedStatus))
                self.zedStatus = self.cam.close()
                raise SystemExit
            else:
                self.runtime_param = sl.RuntimeParameters(enable_point_cloud=False)
        elif not is_on:
            self.zedStatus = self.cam.close()
            print(self.zedStatus)
        else:
            print('camera is already on')

    def check_readings(self):
        """Take a picture if avalible"""
        self.zedStatus = self.cam.grab(self.runtime_param) #run camera
        if self.zedStatus == sl.ERROR_CODE.SUCCESS:
            isnew = True
            self.image_time = timestamp()
            self.cam.retrieve_image(self._image, sl.VIEW.VIEW_LEFT)
            self.cam.retrieve_measure(self._depth, sl.MEASURE.MEASURE_DEPTH)
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
