
# individual detected object
class Detection:
	
	def __init__(self):
		self.frame = 0				# frame number
		self.objID = 0				# object ID
		self.c_x = 0				# x-coordinate center
		self.c_y = 0				# y-coordinate center
		self.w = 0					# width of buoy
		self.h = 0					# height of buoy
		self.time_stamp = None		# time stamp at conclusion of image processing

		# true center of frame
		self.true_x = 360
		self.true_y = 540
        
		# true depth of ZED frame
		self.true_dz = 0

		# center difference
		self.delta_x = 0
		self.delta_y = 0
		self.delta_z = 0

		# bounding box coordinates
		"""
		(x1, y1)----
		|	       |
		|		   |
		----(x2, y2)
		"""
		self.x1 = 0
		self.y1 = 0
		self.x2 = 0
		self.y2 = 0
	
	# passed from detection algorithms
	def write(self, frame_num, objectID, center_x, center_y, width, height, ts, x_one, y_one, x_two, y_two):
		self.frame = frame_num
		self.objID = objectID
		self.c_x = center_x
		self.c_y = center_y
		self.w = width
		self.h = height
		self.time_stamp = ts
		self.x1 = x_one
		self.y1 = y_one
		self.x2 = x_two
		self.y2 = y_two
		
		# convert coordinates
		#self.delta_x = self.true_x - self.c_x
		self.delta_x = self.c_x - self.true_x
		
		#self.delta_y = self.true_y - self.c_y
		self.delta_y = self.c_y - self.true_y

		#* convert dz coordinates

# handles writing all detections
class VisionNode:

	def __init__(self):
		
		self.record = [];
		self.file = open('detections.txt', 'w')
		self.file.write("writing detections ... \n \n")
	
	# closes file after writing completion
	def manage_file(self, close):	
		if (close == True):
			self.file.close()

	# logs all detections
	def log(self, Detection):
		obj_string = ""

		# outputting delta_x, delta_y and delta_z for mission
		obj_string = "[ " + str(Detection.frame) + ", " + str(Detection.objID) + ", " + str(Detection.delta_x) + ", " + str(Detection.delta_y) + ", " + str(Detection.delta_z) + ", " + str(Detection.w) + ", " + str(Detection.h) + ", " + str(Detection.time_stamp) + " ]"
		
		self.file.write(obj_string + "\n")
