import io
import time
import threading
import picamera
from picamera import PiCamera
import numpy as np
import cv2

def processing(image):
    edges = cv2.Canny(image,100,200)
    return

class View(threading.Thread):
    def __init__(self):

        print "View starting"

        # initialize the state
        super(View, self).__init__()
        # this will be used to interact with the caller
        self.called = threading.Event()
        self.terminated = False

        # data structures for images
        self.stream = io.BytesIO()
        self.current_image = None
        self.previous_image = None

        # camera object
        self.camera = self.initialize_camera()

        self.start()

    def initialize_camera(resolution=(400,400),framerate=10):
        camera = PiCamera()
        # let camera warm up!!!!!!!!!!!!!!
        # this is extremely important, readings from sensor
        # need stabilization.
        time.sleep(2)
        print "Initialized camera"
        camera.resolution = resolution
        camera.framerate = framerate
        return camera

    def run(self):
        print "running"
        while(not self.terminated):
            start = time.time()

            # caputure image from camera
            self.camera.capture_sequence(self.stream,use_video_port=True)
            data = np.fromstring(stream.getvalue(),dtype=np.uint8)
            # turn the array into a cv2 image
            self.current_image = cv2.imdecode(data,1)

            # do processing
            processing(self.current_image)

            # save previous image
            self.previous_image = self.current_image

            # reinitialize the stream
            stream.seek(0)
            stream.truncate()

            end = time.time()
            print "processing time: %d secs" % end - start

View()
