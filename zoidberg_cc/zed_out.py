from zoidberg import ZedNode, pause, episode
import cv2

runnum = episode()
zn = ZedNode()
try:
    print("starting up communication with Zed camera")
    zn.isactive(True)
    zn.print_camera_information()
    while True:
        isnew = zn.check_readings()
        if isnew:
            cv2.imshow("image", zn.image)
            cv2.imshow("depth", zn.depth)
            zn.log(runnum)
finally:
    print("Shutting down communication with Zed camera")
    cv2.destroyAllWindows()
    zn.isactive(False)
