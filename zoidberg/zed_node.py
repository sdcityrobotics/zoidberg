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

param = dict(camera_resolution=sl.RESOLUTION.RESOLUTION_HD720,
             depth_mode=sl.DEPTH_MODE.DEPTH_MODE_MEDIUM,
             coordinate_units=sl.UNIT.UNIT_METER,
             camera_fps=10,
             camera_buffer_count_linux=1
        )


class ZedNode:
    """Main communication connection between the ZedCamera and Zoidberg"""
    def __init__(self, input_pipe=None, output_pipes=None):
        """Basic initilization of camera"""
        self.input_pipe = input_pipe
        # make output pipe a list by default
        if not isinstance(output_pipes, (list,)):
            output_pipes = [output_pipes]
        self.output_pipes = output_pipes

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

    def isactive(self, is_on):
        """Turn communication with the zed camera on and off"""
        # Check if we should open the camera or not
        if self.input_pipe is not None:
            print("Input to node is another zed node, not the camera")
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
        else:
            print('camera is already on')

    def check_readings(self):
        """Take a picture if avalible"""
        if self.input_pipe is not None:
            self.serialize()

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
        save_path = os.path.join(episode_name, 'stills')
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        imname = 'img_' + self.image_time + '.jpeg'
        depthname = 'depth_' + self.image_time + '.jpeg'
        self._image.write(os.path.join(save_path, imname))
        # convert from floating point numbers to integers before save
        save_depth = Image.fromarray(self.depth)
        save_depth = save_depth.convert("L")
        save_depth.save(os.path.join(save_path, depthname))

    def serialize(self):
        """serialize or unserialize image data. Used to share data across pipes
        """
        # use a blocking read from the pipe
        if self.input_pipe is not None:

            # check that the pipe exists
            if not os.path.exists(self.input_pipe):
                print("No input pipe exists")
                # continue

            # load data from pipe, update relevant variables
            with open(self.input_pipe, 'rb') as infile:
                pin = pickle.load(infile)
                if len(pin) > 0:
                    self.image_time = pin[0]
                    self.image = pin[1]
                    self.depth = pin[2]

        # write data to any waiting pipes
        if self.output_pipes is not None:
            byte_stream = pickle.dumps([self.image_time,
                                        self.image,
                                        self.depth])
            # assume that there can be more than one output pipe
            for p in self.output_pipes:
                write_pipe(byte_stream, p)
