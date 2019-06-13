import cv2

"""
individual detection object
"""
class Detection:
    """Uniform class for single detection information"""
    def __init__(self):
        """Initilize an empty detection"""
        self.frame_num = None
        self.objectID = None
        self.bb_ul = None
        self.bb_lr = None
        self.time_stamp = None

        # center of frame, assume a fixed frame size
        self.frame_center_x = 360
        self.frame_center_y = 540

        # calculated values
        self.height = None
        self.width = None
        self.center_x = None
        self.center_y = None


    def write(self, frame_num, objectID, time_stamp, bb_ul, bb_lr):
        """Populate detection information"""
        self.frame_num = frame_num
        self.objectID = objectID
        self.time_stamp = time_stamp
        # bounding box coordinates
        """
        (x1, y1)----
        |	       |
        |		   |
        ----(x2, y2)
        bb_ul: bounding box upper left, bb_ul[0] = x1, bb_ul[1] = y1
        bb_lr: bounding box lower right, bb_lr[0] = x2, bb_lr[1] = y2
        """
        self.bb_ul = bb_ul
        self.bb_lr = bb_lr

        # coordinates of center point
        self.width = bb_lr[0] - bb_ul[0]
        self.height = bb_lr[1] - bb_ul[1]

        self.center_x = self.bb_ul[0] + self.width // 2
        self.center_y = self.bb_ul[1] + self.height // 2

        # center difference
        self.delta_x = self.center_x - self.frame_center_x
        self.delta_y = self.center_y - self.frame_center_y
        self.delta_z = 0
    
    def to_string(self):
        """String representation of detection"""
        if self.frame_num is None:
            print('dection is not intitialized')
            return
        # print all detection information to a string
        string_list = ['{:05d}'.format(self.frame_num),
                        '{:03d}'.format(self.objectID),
                        '{:04d}'.format(self.bb_ul[0]),
                        '{:04d}'.format(self.bb_ul[1]),
                        '{:04d}'.format(self.bb_lr[0]),
                        '{:04d}'.format(self.bb_lr[1]),
                        self.time_stamp]
        # put sting list into a comma separated value string
        outstring = ", ".join(string_list)
        return outstring

    def from_string(self, detection_string):
        """Load a detection from string representation"""
        sting_list = detection_string.split(', ')
        if len(sting_list) != 6:
            print('dection string is incorect length')
            return
        # populate detection information from string
        self.frame_num = int(sting_list[0])
        self.objectID = int(sting_list[1])
        self.bb_ul = (int(sting_list[2]), int(sting_list[3]))
        self.bb_lr = (int(sting_list[4]), int(sting_list[5]))

    def draw_box(self, canvas):
        """Draw detection bounding box on input canvas"""
        cv2.rectangle(canvas, self.bb_ul, self.bb_lr, (0, 255, 0), 2)
