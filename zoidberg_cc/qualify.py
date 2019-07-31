from zoidberg import ZedNode, VisionNode, PixhawkNode, Detection, pause, episode
import cv2
from serial import SerialException

runnum = episode()

# Linux address
device = '/dev/ttyACM0'
# Windows address
#device = 'COM3'
pn = PixhawkNode(device)
zn = ZedNode(device)
vn = VisionNode()

# uncomment for activating pixhawk and zed
node_dict = {'pn':pn, 'zn':zn}

drive_count = 0        # drive counter  
gate_c_x = 0           # gate's center x value
gate_c_y = 0           # gate's center y value

frame_c_x = 1280       # frame's center x value
frame_c_y = 360        # frame's center y value

speed_const = 0.2      # speed multiplier, multiplied by distance from target when centering  
depth_const = 0.001    # depth multiplier, multiplied by distance from target when centering
target_depth = 0.3     # target depth

# *** all times for task completion
total_time = 10     # for gate completion
str8_time = 10      # drive straight time
buoy_time = 10      # for hitting the buoy

# for is_timeout - not needed atm
heading_time = 10
depth_time = 10
drive_time = 10

# establish counters and booleans for fully driving through the gate
target_acquired = False
not_at_beginning = False
target_count = 0
end_count = 0

try:
    print('Starting communication with Pixhawk')
    print('Starting communication with Zed camera')
    zn.isactive(True)
    pn.isactive(True)
    
    """is_timeout booleans --> not necessary for the moment
    is_timeout = change_heading(node_dict, runnum, total_time, target_heading)
    is_timeout = change_depth(node_dict, runnum, total_time, target_depth1)
    is_timeout = drive_robot(node_dict, runnum, total_time, speed_forward=forward_speed, speed_side=side_speed)
    """

    while True:
        isnew = zn.check_readings()
        if isnew:
            # attempt to find gate from image
            vn.find_gate(vn.image, vn.depth)
            
            # make sure that something was found
            if (vn.detections[2].center_x ==  None and vn.detections[2].center_y == None):
               # pass if nothing was found in the frame
               print('null')
               
               # continue to drive the robot in general direction
               drive_robot(node_dict, runmnum, total_time, speed_forward=forward_speed, side_speed=0)
               target_count = 0
               target_acquired = False
                
               if (not_at_beginning == True):
                   end_count += 1 
                    
                   # if not at the end but gate was found, now drive straight for awhile
                   if (end_count >= 5):
                       # drive straight for a given amount of time
                       drive_robot(node_dict, runnum, str8_time, speed_forward=forward_speed, side_speed=0)

            else:  
                """Gate was found, do analysis"""
                # obtain the real gate detection
                print('gate found')
                gate_c_x = vn.detections[2].center_x 
                gate_c_y = vn.detections[2].center_y

                # compute side speed and depth values from image for motor commands
                ss_right = ((gate_c_x - frame_c_x) * speed_const)
                ss_left = ((frame_c_x - gate_c_x) * speed_const) 
                d_low = target_depth - ((frame_c_y - gate_c_y) * depth_const)
                d_high = target_depth + ((gate_c_y - frame_c_y) * depth_const)
                
                # make decisions for driving changes
                if (gate_c_x > frame_c_x):
                    drive_robot(node_dict, runnum, total_time, speed_forward=forward_speed, speed_side=ss_right)
                elif (gate_c_x < frame_c_x):
                    drive_robot(node_dict, runnum, total_time, speed_forward=forward_speed, speed_side=ss_left)
                
                # make decisions for depth changes
                if (gate_c_y < frame_c_y):
                    change_depth(node_dict, runnum, total_time, d_low)
                elif (gate_c_y > frame_c_y):
                    change_depth(node_dict, runnum, total_time, d_high)
   
                # increment target (gate finder) counter
                target_count += 1

                # if the gate was found enough times, lock on target                
                if (target_count == 50):
                    target_acquired = True
                    not_at_beginning = True

        # nothing was found, continue and obtain new image for analysis

        """
        if is_timeout:
            print('Reached desired heading')
        else:
            print('Mission timed out')
        """

except SerialException:
    print('Pixhawk is not connected to %s' % device)
    raise
    
finally:
    print('Shutting down communication')
    zn.isactive(False)
    pn.isactive(False)
    cv2.destroyAllWindows()
