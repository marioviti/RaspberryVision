import io
import time
import threading
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

def processing(image):
    edges = cv2.Canny(image,100,200)
    return

def initialize_camera(res=(640, 480),fr=10):
    camera = PiCamera()
    # let camera warm up!!!!!!!!!!!!!!
    # this is extremely important, readings from sensor
    # need stabilization.
    time.sleep(2)
    camera.resolution = res
    camera.framerate = fr
    return camera

class View(threading.Thread):
    def __init__(self):

        print "View starting"

        # initialize the state
        super(View, self).__init__()
        # this will be used to interact with the caller
        self.called = threading.Event()
        self.terminated = False

        # camera object
        self.camera = initialize_camera()

        # data structures for images
        self.stream = PiRGBArray(self.camera)
        self.current_image = None
        self.previous_image = None

        self.start()

    def run(self):
        print "running"
        while(not self.terminated):
            start = time.time()

            # caputure image from camera
            self.camera.capture(self.stream,format='bgr',use_video_port=True)

            # turn the stream to array
            self.current_image = self.stream.array

            # do processing
            processing(self.current_image)

            # save previous image
            self.previous_image = self.current_image

            # reinitialize the stream
            self.stream.seek(0)
            self.stream.truncate()

            end = time.time()
            delta = (end - start)
            print "processing time: %f secs" % delta

View()
