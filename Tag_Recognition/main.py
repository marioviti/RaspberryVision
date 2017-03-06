import time
import signal
import cv2
import numpy as np

from Tag_Detector import Tag_Detector
import Settings
import tag_recognition

RUNNING = True

def signal_handler(signal, frame):
    print "CTRL-C"
    global RUNNING
    RUNNING = False

if __name__ == '__main__':
    """
    This program is designed to recognize Tags.
    """
    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, signal_handler)
    tag_detector = Tag_Detector()
    tag_detector.start()
    print "hallowing camera to warm up"
    time.sleep(4)
    print "let's start!!!"
    while(RUNNING):
        orientation = tag_detector.retrieve_tag_orientations()
        if orientation!=[]:
            print orientation
    tag_detector.shutdown()
    print "good bye"
