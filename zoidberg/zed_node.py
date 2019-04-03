"""
Zed Camera
==========
Standard interface between Zoidberg and zed camera.
"""
import os
import pyzed.sl as sl
from zoidberg import timestamp
from numpy import savez as array_save
from PIL import Image

param = dict(camera_resolution=sl.RESOLUTION.RESOLUTION_HD720,
             depth_mode=sl.DEPTH_MODE.DEPTH_MODE_MEDIUM,
             coordinate_units=sl.UNIT.UNIT_METER,
             camera_fps=10,
             camera_buffer_count_linux=1
        )


class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self, writeonly=False):
        """Basic initilization of camera"""
        self.writeonly = writeonly
        # create a save directory, drop ms from datestring
        self.savedir = '_'.join(timestamp().split('_')[:-1])
        self.savedir = os.path.join(os.getcwd(), self.savedir)
        self.init = sl.InitParameters(**param)
        self.cam = sl.Camera()
        self.zed_param = None
        self.zedStatus = None
        self.runtime_param = None
        self._image = sl.Mat()
        self._depth = sl.Mat()
        self.image = None
        self.depth = None
        self.max_depth = 10  # max depth in map, meters
        self.image_time = None

    def isactive(self, is_on):
        """Turn communication with the zed camera on and off"""
        if self.writeonly:
            raise(ValueError('Node set as write only'))

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
        if not self.cam.is_opened():
            print('Camera is not open')
            return

        self.zedStatus = self.cam.grab(self.runtime_param) #run camera
        if self.zedStatus == sl.ERROR_CODE.SUCCESS:
            isnew = True
            self.image_time = timestamp()
            self.cam.retrieve_image(self._image, sl.VIEW.VIEW_LEFT)
            self.cam.retrieve_measure(self._depth, sl.MEASURE.MEASURE_DEPTH)
            self.image = self._image.get_data()
            self.depth = self._depth.get_data()
            # remove nans from depth map
            self.depth[np.isnan(depth)] = self.max_depth
            # limit maximal value of depth map
            self.depth[self.depth > self.max_depth] = self.max_depth
        else:
            isnew = False
        return isnew

    def log(self, episode_name):
        """Save current image to file"""
        save_path = os.path.join(episode_name, 'stills')
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        imname = 'img_' + self.image_time + '.jpeg'
        depthname = 'depth_' + self.image_time + '.npz'
        self._image.write(os.path.join(save_path, imname))
        # convert from floating point numbers to integers before save
        save_depth = depth * 255 / self.max_depth
        save_depth = save_depth.astype(np.int8)
        save_depth = Image.fromarray(save_depth)
        save_depth = save_depth.convert("L")
        save_depth.save(os.path.join(save_path, depthname))