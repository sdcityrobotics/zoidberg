from zoidberg import ZedNode, pause, episode
import cv2
from zoidberg import VisionNode

runnum = episode()
# specifying a recording for testing
zn = ZedNode('19_145_10_57_14')
#zn = ZedNode()
vn = VisionNode()

try:
    print("starting up communication with Zed camera")
    zn.isactive(True)
    while True:
        isnew = zn.check_readings()
        if isnew:
            # obtain image and log detections
            cv2.imshow("image", zn.image)
            vn.find_gate(zn.image, zn.depth)
            for detection in vn.detections:
                # draw detection bounding box
                """verify that there are objects to detect first"""
                detection.draw_box(zn.image)
            cv2.imshow("depth", zn.depth)
            cv2.imshow("bb", zn.image)
            cv2.waitKey(100)
            vn.log(runnum)
        if not isnew:
            break

finally:
    # close file
    print("Shutting down communication with Zed camera")
    zn.isactive(False)
    cv2.destroyAllWindows()
