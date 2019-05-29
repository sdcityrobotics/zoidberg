import cv2
import datetime
import numpy as np
from vision_node import Detection, VisionNode

def finder(img, frame_num):

	time_stamp = str(datetime.datetime.now())
	img_color = img.copy()
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# initial function scan to find all contours
	scan_img = cv2.Sobel(img, cv2.CV_8U, 0, 1, ksize=5)
	scan_img = cv2.threshold(scan_img, 200, 255, cv2.THRESH_BINARY)[1]
	scan_img = cv2.erode(scan_img, None, iterations=1)
	scan_img = cv2.dilate(scan_img, None, iterations=1)

	# find contours 
	contours = cv2.findContours(scan_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	contours = contours[1];

	# set the minimum and maximum distance ratios for valid buoys
	ratioMax = 0.5
	ratioMin = 0.2

	# initialize buoy array and counter
	buoys = []
	count = 0

	for contour in contours:
		# if the length of the contour is long enough to be a potential buoy
		if(len(contour) > 45):	
			# find coordinates in the frame for buoy validation
			max_Pt = [9999999, 9999999] 	# highest y point, huge values for safety
			endPt1 = [9999999999, 0] 		# the highest y point with lowest x coordinate
			endPt2 = [-1, 0]				# point with the highest x coordinate

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
				ratio = (h/(2*w))
			else:
				ratio = 0

			if ((ratio >= ratioMin) and (ratio <= ratioMax)):
				buoys.append(contour)
				count += 1

	# initialize object array and ID count 
	obj_ID = 1
	objs = []

	for buoy in buoys:
		# find inital (x, y) coordinates and radius of contour
		(x,y),radius = cv2.minEnclosingCircle(buoy)
		x_coord = int(x)
		y_coord = int(y)
		center = (x_coord, y_coord)
		radius = int(radius)

		# *** remove contours that are just noise ***
		# find arbitrary distance away from the center
		dist = (radius*1)/4

		# for storing pixels that could potentially be noise
		outliers = 0; 

		for point in buoy:
			point = point[0]

			# determine if a pixel is an outlier based on y-coord position from center
			if (point[1] > center[1] and (point[0] > center[0] - dist and \
					point[0] < center[0] + dist)):
				outliers += 1

		# if too many outliers were found, it's noise
		if (outliers > 1):
			continue

		# creating width and height for object
		# *** width and height are calculated the same for bounding boxes(squares)
		width = radius * 2

		x_1 = x_coord + radius
		y_1 = y_coord + radius
		x_2 = x_coord - radius
		y_2 = y_coord - radius

		# draw bounding box for mission labeling
		cv2.rectangle(img_color, (x_1, y_1),
						(x_2, y_2), (255, 0, 0), 2)

		str_x = str(x_coord)
		str_y = str(y_coord)
		cv2.putText(img_color, str_x + ', ' + str_y, (x_coord, y_coord),
					cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

		# create class instance and store info
		# inputting width = height into object for now
		detection = Detection()
		detection.write(frame_num, obj_ID, x_coord, y_coord, width, width, time_stamp, x_1, y_1, x_2, y_2)
		objs.append(detection)
		obj_ID += 1
	
		# output image to a file for analysis
		cv2.imshow("img", img_color)

	return objs
