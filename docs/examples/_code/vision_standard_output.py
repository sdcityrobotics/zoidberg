"""
Standard output to use for testing mission

Each vision output will look like:

image_ID, object_ID, center_x, center_y, width, height, procssing_timestamp

Example Image
-----------> x
|  ..........................................
|  ..........................................
|  ..........................................
|  ..........................................
v  ...........<----w---->....................
y  ..........................................
    .......^...-----------....................
    .......|...|.........|....................
    .......h...|....C....|....................
    .......|...|.........|....................
    .......v...-----------....................
    ..........................................
    ..........................................

timestamp format: 19_067_11_50_05_561
year_JulianDay_Hour_Min_Sec_MS
"""


import time
import datetime
from zoidberg import utils

object_001 = ['001', '463', '0432', '034', '056']
object_002 = ['002', '023', '0123', '347', '021']
object_003 = ['003', '765', '1002', '745', '102']

# Each image will have a time based ID
image_ID = 'img_' + utils.timestamp()

def standard_output(detection_in):
    """Return up to three objects"""
    processing_timestamp = utils.timestamp()
    tstring = [image_timestamp] + detection_in + [processing_timestamp]
    detect_string = ", ".join(tstring)
    return detect_string

for ob in [object_001, object_002, object_003]:
    print(standard_output(ob))
    time.sleep(1)
