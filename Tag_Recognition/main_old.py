import time
import signal
import cv2
import numpy as np

import Camera_Controller
import Settings
import tag_recognition

RUNNING = True

def signal_handler(signal, frame):
    print "CTRL-C"
    global RUNNING
    RUNNING = False

def pre_processing_image(image):
    """
        this operations block the image acquisition
    """
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return imgray

if __name__ == '__main__':
    """
    This program is designed to recognize Tags.
    """
    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, signal_handler)
    camera_controller = Camera_Controller.Camera_Controller()
    camera_controller.start()
    # calibration loop

    area_ratio = Settings.Tag_Settings['area_ratio']
    contours_tag = []
    extsLeft,extsRight,extsTop,extsBottom = None, None, None, None
    image, contours, tag_ids = None, None, None
    while(RUNNING):
        if camera_controller.processing_buffer!=None:
            with camera_controller.processing_buffer_lock:
                imgray = pre_processing_image(camera_controller.processing_buffer)
            contours_tag, tag_ids = tag_recognition.detecting_tag(imgray,area_ratio)
            extsLeft,extsRight,extsTop,extsBottom = tag_recognition.countours_extreme_points(contours_tag)
            for i in range(len(extsLeft)):
                ori = tag_recognition.triangle_orientation(extsLeft[i],extsRight[i],extsTop[i],extsBottom[i])
                if ori == 1:
                    print "right"
                else:
                    print "left"
    image = camera_controller.processing_buffer
    camera_controller.shutdown()

    # experiment
    # tell triangle orientation
    # triangle_edges = extL[0], extR[0], extT[0], extB[0]
    # 2 cases < > 2 sub cases /\ V
    # case 1 if extLy < extRx
    # case 2 if extLy and etxRy and extTy are similar
    for i in range(len(extsLeft)):
        ori = tag_recognition.triangle_orientation(extsLeft[i],extsRight[i],extsTop[i],extsBottom[i])
        if ori == 1:
            print "right"
        else:
            print "left"
    for extL in extsLeft:
        cv2.circle(image, tuple(extL) , 8, (0, 0, 255), -1)
    for extR in extsRight:
        cv2.circle(image, tuple(extR), 8, (0, 255, 0), -1)
    for extT in extsTop:
        cv2.circle(image, tuple(extT), 8, (255, 255, 0), -1)
    for extB in extsBottom:
        cv2.circle(image, tuple(extB), 8, (255, 0, 0), -1)
    cv2.drawContours(image, contours_tag, -1, (255,0,0), 3)
    cv2.imshow('image',image)
    cv2.waitKey(0) # press any key
    cv2.destroyAllWindows()
