from zoidberg import ZedNode, pause, episode
import cv2

runnum = episode()
zn = ZedNode()

# commented because we dont have a vision node yet
# vn = VisionNode()

try:
    print("starting up communication with Zed camera")
    zn.isactive(True)
    while True:
        isnew = zn.check_readings()
        if isnew:
            cv2.imshow("image", zn.image)
            cv2.imshow("depth", zn.depth)
            cv2.waitKey(1)
            ### Run detection

            #vn.detect_buoys(zn.image)

            ### loop through detections and draw them on image

            #for detect in vn.detections:
                ### code to draw bounding box on image and depth feed
                # pass

            zn.log(runnum)
            #vn.log(runnum)

finally:
    print("Shutting down communication with Zed camera")
    cv2.destroyAllWindows()
    zn.isactive(False)
