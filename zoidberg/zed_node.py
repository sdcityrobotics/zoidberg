"""
Zed Camera
==========
Standard interface between Zoidberg and zed camera.
"""
import os

# Don't require zed library if you don't need it
"""
try:
    import pyzed.sl as sl
except ModuleNotFoundError:
    pass
"""

from zoidberg import timestamp
import numpy as np
import cv2

class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self, input_dir=None):
        """Basic initilization of camera"""
        # zed node can be setup to read from saved videos
        self.input_dir = input_dir
        self.image_reader = None
        self.depth_reader = None

        # These are the variables that will be used by mission
        self.image_time = None
        self.image = None
        self.depth = None

        # set up camera only if we need to work with live feed
        if input_dir is None:
            # initilization information for camera
            cam_param = dict(camera_resolution=sl.RESOLUTION.RESOLUTION_HD720,
                             depth_mode=sl.DEPTH_MODE.DEPTH_MODE_MEDIUM,
                             coordinate_units=sl.UNIT.UNIT_METER,
                             camera_fps=10,
                             camera_buffer_count_linux=1)
            self.init = sl.InitParameters(**cam_param)
            self.cam = sl.Camera()
            self._image = sl.Mat()
            self._depth = sl.Mat()
        else:
            self.init = None
            self.cam = None
            self._image = None
            self._depth = None

        self.zed_param = None
        self.zedStatus = None
        self.runtime_param = None
        self.max_depth = 10  # max depth in map, meters
        self.codec = cv2.VideoWriter_fourcc(*'DIVX')
        self.depth_writer = None
        self.image_writer = None

    def isactive(self, is_on):
        """Turn communication with the zed camera on and off"""
        # Check if we should open the camera or not
        if self.input_dir is not None:
            if is_on:
                vid_path = os.path.join(self.input_dir, 'images.avi')
                depth_path = os.path.join(self.input_dir, 'depth.avi')
                self.image_reader = cv2.VideoCapture(vid_path)
                self.depth_reader = cv2.VideoCapture(depth_path)
                print('Video opened')
            else:
                self.image_reader.release()
                self.depth_reader.release()
            return

        # Once we get to this part of the code we are working with zed camera
        if is_on and not self.cam.is_opened():
            self.zedStatus = self.cam.open(self.init)
            if self.zedStatus != sl.ERROR_CODE.SUCCESS:
                print(repr(self.zedStatus))
                self.zedStatus = self.cam.close()
                raise SystemExit
            self.runtime_param = sl.RuntimeParameters(enable_point_cloud=False)
        elif not is_on:
            self.zedStatus = self.cam.close()
            if self.depth_writer is not None:
                self.depth_writer.release()
                self.image_writer.release()
                self.depth_writer = None
                self.image_writer = None
        else:
            print('camera is already on')

    def check_readings(self):
        """Take a picture if avalible"""
        if self.input_dir is not None:
            #get image from video
            ret, image = self.image_reader.read()
            if ret:
                self.image = image
            #get depth from video
            ret, depth = self.depth_reader.read()
            if ret:
                self.depth = depth
            return ret

        # Once we get to this part of the code we are working with zed camera
        if not self.cam.is_opened():
            print('Camera is not open')
            return

        self.zedStatus = self.cam.grab(self.runtime_param) #run camera
        if self.zedStatus == sl.ERROR_CODE.SUCCESS:
            isnew = True
            self.image_time = timestamp()
            self.cam.retrieve_image(self._image, sl.VIEW.VIEW_LEFT)
            self.cam.retrieve_measure(self._depth, sl.MEASURE.MEASURE_DEPTH)
            # save image
            image = self._image.get_data()
            # first convert from RGBA to RGB
            self.image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            # save depth map
            self.depth = self._depth.get_data()
            # remove nans from depth map
            self.depth[np.isnan(self.depth)] = self.max_depth
            # limit maximal value of depth map
            self.depth[self.depth > self.max_depth] = self.max_depth
            # convert from float to int8
            self.depth = self.depth * 255 / self.max_depth
            self.depth = self.depth.astype(np.uint8)
        else:
            isnew = False
        return isnew

    def log(self, episode_name):
        """Save current image to file"""
        if self.image is None:
            return

        if self.input_dir is not None:
            return

        # make sure save folder exists
        if not os.path.isdir(episode_name):
            os.makedirs(episode_name)

        if self.image_writer is None:
            size = (self.image.shape[1], self.image.shape[0])
            video_name = os.path.join(episode_name, 'images.avi')
            self.image_writer = cv2.VideoWriter(video_name, self.codec, 10, size, True)

        if self.depth_writer is None:
            size = (self.depth.shape[1], self.depth.shape[0])
            depth_name = os.path.join(episode_name, 'depth.avi')
            self.depth_writer = cv2.VideoWriter(depth_name, self.codec, 10, size, False)

        # save the current image
        self.image_writer.write(self.image)
        self.depth_writer.write(self.depth)
