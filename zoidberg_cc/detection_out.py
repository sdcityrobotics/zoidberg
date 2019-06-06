from zoidberg import ZedNode, pause, episode
import cv2
from zoidberg import VisionNode

runnum = episode()
# specifying a recording for testing
zn = ZedNode('19_145_10_57_14')
vn = VisionNode()
frame_num = 0

try:
    print("starting up communication with Zed camera")
    zn.isactive(True)
    while True:
        isnew = zn.check_readings()
        if isnew:
            # obtain image and log detections
            cv2.imshow("image", zn.image)
            vn.find_buoy(zn.image)
            for detection in vn.detections:
                # this should draw the detections on the image
                pass
            #cv2.imshow("depth", zn.depth)
            cv2.waitKey(100)

        if not isnew:
            break
finally:
    # close file
    vn.manage_file(True)
    print("Shutting down communication with Zed camera")
    zn.isactive(False)
    cv2.destroyAllWindows()