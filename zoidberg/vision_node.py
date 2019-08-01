"""
===========
Vision Node
===========
Handles detections, logs and stores latest values
"""
import os
import cv2

import datetime
import numpy as np

from zoidberg import Detection
from zoidberg.utils import timestamp

class VisionNode:
    """Node used by mission to handle detections"""
    def __init__(self):
        """Basic initialization"""
        self.detections = None
        self.frame_num = 0
        self.buoy_ID = 1  # integer buoy detection ID
        self.r_gate_ID = 2  # integer right gate detection ID
        self.l_gate_ID = 3  # integer left gate detection ID
        self.g_gate_ID = 4  # integer full gate detection ID

    def buoy_detection(self, ts, ul, lr):
        """Create Detection class instance to store info"""
        detection = Detection()
        detection.write_buoy(self.frame_num,
                        self.buoy_ID,
                        ts,
                        ul,
                        lr)
        self.detections.append(detection)

    def gate_detection(self, gate_legs):
        """Gate detection object creation"""
        # r_g = right gate leg
        # l_g = left gate leg 
        # gate = top gate bar
        # ul = upper left, br = bottom right
        r_g_ul_x = None
        r_g_ul_y = None
        r_g_br_x = None
        r_g_br_y = None
        r_g_w = None
        r_g_h = None
        l_g_ul_x = None
        l_g_ul_y = None
        l_g_br_x = None
        l_g_br_y = None
        l_g_w = None
        l_g_h = None
        gate_ul_x = None
        gate_ul_y = None
        gate_br_x = None
        gate_br_y = None
        gate_w = None
        gate_h = None

        r = Detection()
        l = Detection()
        g = Detection()

        if (gate_legs[0].x > gate_legs[1].x):
            # (x, y, w, h)1 = right gate --> [0]
            r_g_ul_x = gate_legs[0].x
            r_g_ul_y = gate_legs[0].y
            r_g_w = gate_legs[0].w
            r_g_h = gate_legs[0].h
            r_g_br_x = r_g_ul_x + r_g_w
            r_g_br_y = r_g_ul_y + r_g_h
            l_g_ul_x = gate_legs[1].x
            l_g_ul_y = gate_legs[1].y
            l_g_w = gate_legs[1].w
            l_g_h = gate_legs[1].h
            l_g_br_x = l_g_ul_x + l_g_w
            l_g_br_y = l_g_ul_y + l_g_h

        else:
            # (x, y, w, h)1 = right gate --> [1]
            l_g_ul_x = gate_legs[0].x
            l_g_ul_y = gate_legs[0].y
            l_g_w = gate_legs[0].w
            l_g_h = gate_legs[0].h
            l_g_br_x = l_g_ul_x + l_g_w
            l_g_br_y = l_g_ul_y + l_g_h
            r_g_ul_x = gate_legs[1].x
            r_g_ul_y = gate_legs[1].y
            r_g_w = gate_legs[1].w
            r_g_h = gate_legs[1].h
            r_g_br_x = r_g_ul_x + r_g_w
            r_g_br_y = r_g_ul_y + r_g_h

        gate_ul_x = l_g_ul_x
        gate_ul_y = l_g_ul_y
        gate_br_x = r_g_br_x
        gate_br_y = r_g_br_y
        gate_w = int(abs(gate_ul_x - gate_br_x))
        gate_h = int(abs(gate_ul_y - gate_br_y))

        """ 
        cv2.rectangle(origin, (gate_ul_x, gate_ul_y), (gate_br_x, gate_br_y), \
                     (255, 255, 255), 10)
        cv2.imshow('origin', origin)
        """

        r.write_gate(self.frame_num, self.r_gate_ID, timestamp(), r_g_ul_x, r_g_ul_y, r_g_br_x, r_g_br_y, \
                     r_g_w, r_g_h)

        l.write_gate(self.frame_num, self.l_gate_ID, timestamp(), l_g_ul_x, l_g_ul_y, l_g_br_x, l_g_br_y, \
                     l_g_w, l_g_h)

        g.write_gate(self.frame_num, self.g_gate_ID, timestamp(), gate_ul_x, gate_ul_y, gate_br_x, gate_br_y, \
                     gate_w, gate_h)
        
        self.frame_num += 1
        self.detections.append(r)
        self.detections.append(l)
        self.detections.append(g)

    def find_buoy(self, img):
        """Find objects by contour"""
        # set the minimum and maximum distance ratios for valid buoys
        ratioMax = 0.5
        ratioMin = 0.2

        # Step the frame number
        self.frame_num += 1

        # make copies of images
        img_color = img.copy()
        scan_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # initial function scan to find all contours
        scan_img = cv2.Sobel(scan_img, cv2.CV_8U, 0, 1, ksize=5)
        scan_img = cv2.threshold(scan_img, 200, 255, cv2.THRESH_BINARY)[1]
        scan_img = cv2.erode(scan_img, None, iterations=1)
        scan_img = cv2.dilate(scan_img, None, iterations=1)


        # find contours
        contours = cv2.findContours(scan_img,
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[1]

        # initialize buoy array and counter
        buoys = []

        # loop through found contours to make decisions
        for contour in contours:
            # if the length of the contour is long enough to be a potential buoy
            if (len(contour) > 45):

                # find coordinates in the frame for buoy validation
                max_Pt = [9999999, 9999999]  # highest y point, huge values for safety
                endPt1 = [9999999999, 0]  # the highest y point with lowest x coordinate
                endPt2 = [-1, 0]  # point with the highest x coordinate

                for Point in contour:
                    # temporary coordinates for comparison
                    temp_y = Point[0][1]
                    temp_x = Point[0][0]

                    # make decision based on location of temporary x and y coords
                    if (temp_y < max_Pt[1]):
                        max_Pt = Point[0]
                    if (temp_x < endPt1[0]):
                        endPt1 = Point[0]
                    if (temp_x > endPt2[0]):
                        endPt2 = Point[0]

                # store endPt1's coordinates into finalEndPt for comparison
                finalEndPt = endPt1;
                if (endPt1[1] > endPt2[1]):
                    finalEndPt = endPt2;

                # calculate width and height of contour
                w = abs(max_Pt[0] - finalEndPt[0])
                h = abs(max_Pt[1] - finalEndPt[1])

                # compute ratio necessary for a contour to be considered a buoy,
                # noise can still be considered a buoy
                if (w != 0):
                    ratio = (h / (2 * w))
                else:
                    ratio = 0

                if ratio >= ratioMin and ratio <= ratioMax:
                         buoys.append(contour)


        # initialize object array and ID count
        self.detections = []

        for buoy in buoys:
            # find inital (x, y) coordinates and radius of contour
            (x,y), radius = cv2.minEnclosingCircle(buoy)
            x_coord = int(x)
            y_coord = int(y)
            center = (x_coord, y_coord)
            radius = int(radius)

            # *** remove contours that are just noise ***
            # find arbitrary distance away from the center
            dist = radius / 4

            # for storing pixels that could potentially be noise
            outliers = 0;

            for point in buoy:
                point = point[0]
                # determine if a pixel is an outlier based on y-coord position from center
                if point[1] > center[1] and (point[0] > center[0] - dist and \
                                    point[0] < center[0] + dist):
                    outliers += 1

            # if too many outliers were found, it's noise
            if (outliers > 1):
                continue

            # compute bounding boxes
            bb_ul = (x_coord - radius, y_coord - radius)
            bb_lr = (x_coord + radius, y_coord + radius)

            # relay information to detection creator
            self.buoy_detection(timestamp(),
                                  bb_ul,
                                  bb_lr)

    def find_rect(self, image, depth):
        """Single rectangular buoy detection"""
        markers = 0
        threshold = 10

        # find buoy by changing blue channel threshold
        while (np.amax(markers) == 0):
            threshold += 5
            temp_t, img = cv2.threshold(image[:,:,0], threshold, 255, cv2.THRESH_BINARY_INV)
            cv2.imshow('img', img)
            _, markers = cv2.connectedComponents(img)

        # define kernal and remove noise
        kernal = np.ones((5,5), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernal)
        img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernal)

        # get pixels of buoy and relay information
        nonzero = cv2.findNonZero(img)
        x = 0
        y = 0
        w = 0
        h = 0
        x, y, w, h = cv2.boundingRect(nonzero)

        # determine if detected object is ideal
        if ((x != 0 and y != 0) or (h > 20 and w > 20)):
            # ideal detected object was found
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            x_c = int(x)
            y_c = int(y)
            h_c = int(h)
            w_c = int(w)
            bb_ul = (x_c - w_c, y_c - h_c)
            bb_lr = (x_c + w_c, y_c + h_c)
            self.detections = []
            self.frame_num += 1
            self.buoy_detection(timestamp(), bb_ul, bb_lr)

        else:
           self.detections = None
           pass

        
    def find_gate(self, image, depth):
        """Gate detection"""
        """Gate leg class"""
        class GateLeg:
            def __init__(self):
                self.x = None
                self.y = None
                self.w = None
                self.h = None

            def log(self, x_c, y_c, w_c, h_c):
                self.x = x_c
                self.y = y_c
                self.w = w_c
                self.h = h_c

            # temporary analysis print
            def print_leg(self):
                print(str(self.x) + ', ' + str(self.y))

        # smooth image with alternative closing/opening by adjusting kernel
        morph = image.copy()
        original = image.copy()
        origin = image.copy()
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

        # take morphological gradient
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        gradient_image = cv2.morphologyEx(morph, cv2.MORPH_GRADIENT, kernel)

        # split the gradient image into channels
        image_channels = np.split(np.asarray(gradient_image), 3, axis=2)
        channel_height, channel_width, _ = image_channels[0].shape

        # apply Otsu threshold to each channel
        for i in range(0, 3):
            _, image_channels[i] = cv2.threshold(~image_channels[i], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
            image_channels[i] = np.reshape(image_channels[i], newshape=(channel_height, channel_width, 1))

        # merge channels
        image_channels = np.concatenate((image_channels[0], image_channels[1], image_channels[2]), axis=2)

        # create result of low/high thresholds
        low = np.array([120, 120, 0])
        high = np.array([255, 255, 0])
        mask = cv2.inRange(image_channels, low, high)
        result = cv2.bitwise_and(image_channels, image_channels, mask=mask)

        # isolate potential rectangles
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # find vertical leg lines
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
        vertical = cv2.erode(thresh, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)

        # form solid leg lines and get contours
        kernel = np.ones((45,45),np.uint8)
        close = cv2.morphologyEx(vertical, cv2.MORPH_CLOSE, kernel)
        im2, contours, hierarchy = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # initialize constants and variables
        main = True
        adjust = True
        min_area = 20*20
        param = 0.60
        gate_legs = []
        self.detections = []

        while main:
            # if parameter adjustment is needed
            if (adjust == False):
                param -= 0.10
                if (param < 0):
                    # nothing was found
                    print('null')
                    self.detections = None
                    main = False

                adjust = True

            # draw contours with area bigger than a minimum and being rectangular
            for contour in contours:
                x = 0
                y = 0
                w = 0
                h = 0
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)

                # validate found area
                if (area > (w * h * param) and area > min_area):
                    # store potenial gate leg
                    leg = GateLeg()
                    leg.log(x, y, w, h)
                    gate_legs.append(leg)

            final_gate_legs = []
            count = 0
            fg_count = 0
            # verify if there were more than two 'legs' found
            if (len(gate_legs) > 2):
                """find the outlier/reflection"""
                x_temp = gate_legs[0].x
                y_temp = gate_legs[0].y
                count = 1
                flag = True

                while flag:
                    # compare next potential leg to original
                    if ((abs(x_temp - gate_legs[count].x) > 100) and (abs(y_temp - \
                            gate_legs[count].y) < 50)):
                        # a good match was found
                        final_gate_legs.append(gate_legs[count])
                        count += 1
                        if (count > len(gate_legs)):
                            # end of list was reached
                            flag = False
                        else:
                            # add original to the final list, eliminating the outlier
                            final_gate_legs.append(gate_legs[0])
                            if ((count + 1) == len(gate_legs)):
                                flag = False
                            else:
                                # keep finding reflections/outliers
                                x_temp = final_gate_legs[fg_count].x
                                y_temp = final_gate_legs[fg_count].y
                                fg_count += 1
                                count += 1
                    else:
                        # more than two were found, but too small
                        flag = False

                # if both legs were found
                if (len(final_gate_legs) == 2):
                    self.gate_detection(final_gate_legs)
                    main = False

                else:
                    # adjust param at the beginning and start over
                    adjust = False

            # if two legs were originally found
            if (len(gate_legs) == 2):
                self.gate_detection(gate_legs)
                main = False

            else:
                # adjust parameter and start over
                adjust = False

        """analysis images
        cv2.imshow("original", original)
        cv2.imshow("line results", im)
        cv2.imshow('result', result)
        cv2.imshow('image', image_channels)
        """

    def log(self, episode_name):
        """Save current detections to file"""

        # make sure there is something to save
        if self.detections is None:
            return

        # make sure save folder exists
        if not os.path.isdir(episode_name):
            os.makedirs(episode_name)

        save_name = os.path.join(episode_name, 'vision_log.txt')

        # append all detections to file
        with open(save_name, 'a') as f:
            for detec in self.detections:
                f.write(detec.to_string())
                f.write('\n')
