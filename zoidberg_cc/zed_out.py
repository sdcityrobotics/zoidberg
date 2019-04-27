from zoidberg import ZedNode, pause, episode
import cv2

runnum = episode()
zn = ZedNode()
try:
    print("starting up communication with Zed camera")
    zn.isactive(True)
    while True:
        isnew = zn.check_readings()
        if isnew:
            cv2.imshow("image", zn.image)
            cv2.imshow("depth", zn.depth)
            cv2.waitKey(100)
            zn.log(runnum)
finally:
    print("Shutting down communication with Zed camera")
    cv2.destroyAllWindows()
    zn.isactive(False)
