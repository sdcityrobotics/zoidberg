"""
Zed Camera
==========
Standard interface between Zoidberg and zed camera.
"""
import os
import pyzed.sl as sl
from zoidberg import timestamp, write_pipe
from numpy import savez as array_save
import pickle
from PIL import Image
import numpy as np
import cv2

param = dict(camera_resolution=sl.RESOLUTION.RESOLUTION_HD720,
             depth_mode=sl.DEPTH_MODE.DEPTH_MODE_MEDIUM,
             coordinate_units=sl.UNIT.UNIT_METER,
             camera_fps=10,
             camera_buffer_count_linux=1
        )

class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self, input_file=None):
        """Basic initilization of camera"""
        self.input_file = input_file
        self.vid = None
        self.dep = None

        # These are the variables that will be shared across all zed nodes
        self.image_time = None
        self.image = None
        self.depth = None

        # These variables are used only in the zed node opening the camera
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
        self.max_depth = 10  # max depth in map, meters
        self.codec = cv2.VideoWriter_fourcc(*'DIVX')
        self.depth_writer = None
        self.image_writer = None

    def isactive(self, is_on):
        """Turn communication with the zed camera on and off"""
        # Check if we should open the camera or not
        if self.input_file is not None:
            if is_on:
                self.vid = cv2.VideoCapture(self.input_file + '\\video.avi')
                self.dep = cv2.VideoCapture(self.input_file + '\\depth.avi')
                print('Video opened')
            else:
                self.vid.release()
                self.dep.release()
            return

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
            self.depth_writer = None
            self.image_writer = None
        else:
            print('camera is already on')

    def check_readings(self):
        """Take a picture if avalible"""
        if self.input_file is not None:
            #get image from video
            ret, image = self.vid.read()
            if ret:
                self.image = image
            #get depth from video
            ret, depth = self.dep.read()
            if ret:
                self.depth = depth
            return

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
            self.depth[np.isnan(self.depth)] = self.max_depth
            # limit maximal value of depth map
            self.depth[self.depth > self.max_depth] = self.max_depth
            # convert from float to int8
            self.depth = self.depth * 255 / self.max_depth
            self.depth = self.depth.astype(np.uint8)
            #self.serialize()
        else:
            isnew = False
        return isnew

    def log(self, episode_name):
        """Save current image to file"""
        if not self.cam.is_opened():
            return
        
        save_path = os.path.join(episode_name, 'stills')
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
            
        if self.image_writer is None:
            self.image_writer = cv2.VideoWriter(save_path, self.codec, 10, size)
        if self.depth_writer is None:
            self.depth_writer = cv2.VideoWriter(save_path, self.codec, 10, size)
            
        imname = 'img_' + self.image_time + '.jpeg'
        depthname = 'depth_' + self.image_time + '.jpeg'
        self._image.write(os.path.join(save_path, imname))
        # convert from floating point numbers to integers before save
        save_depth = Image.fromarray(self.depth)
        save_depth = save_depth.convert("L")
        save_depth.save(os.path.join(save_path, depthname))
