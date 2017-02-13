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

def initialize_camera(res=(640, 480),fr=30):
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
        #self.stream = PiRGBArray(self.camera)
        self.streams = [ io.BytesIO(), io.BytesIO() ]
        self.current_image = None
        self.previous_image = None

        self.start()

    def streams_generator(self):
        for stream in self.streams:
            yield stream

    def run(self):
        print "running"
        while(not self.terminated):
            start = time.time()

            # caputure image from camera
            #self.camera.capture(self.stream,format='bgr',use_video_port=True)
            self.camera.capture_sequence(self.streams_generator(),use_video_port=True)

            data = np.fromstring(self.stream[0].getvalue(),dtype=np.uint8)
            self.previous_image = cv2.imdecode(data,1)

            data = np.fromstring(self.stream[1].getvalue(),dtype=np.uint8)
            self.current_image = cv2.imdecode(data,1)
            # turn the stream to array
            #self.current_image = self.stream.array
            end = time.time()
            delta = (end - start)
            print "capturing time: %f secs" % delta

            start = time.time()
            # do processing
            processing(self.previous_image)
            processing(self.current_image)

            # save previous image
            self.previous_image = self.current_image

            # reinitialize the stream
            self.stream[0].seek(0)
            self.stream[0].truncate()

            self.stream[1].seek(0)
            self.stream[1].truncate()

            end = time.time()
            delta = (end - start)
            print "processing time: %f secs" % delta

View()
