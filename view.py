import io
import time
import threading
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

shutdown = False

def processing(image):
    global shutdown
    ##edges = cv2.Canny(image,100,200)
    cv2.imshow("image",image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        shutdown = True
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
    def __init__(self, buffering_size=5):
        print "View starting"

        # initialize the state
        super(View, self).__init__()
        self.buffering_size = buffering_size
        self.called = threading.Event()
        self.terminated = False

        # camera object
        self.camera = initialize_camera()

        self.streams = []
        self.images = []
        self.initialize_streams()
        # data structures for images

        self.start()


    def initialize_streams(self):
        for i in xrange(self.buffering_size):
            self.streams += [ io.BytesIO() ]
            self.images += [ None ]


    def streams_generator(self):
        """
            yielding the generators for our streams
        """
        for stream in self.streams:
            yield stream

    def run(self):
        print "running"
        while(not self.terminated and not shutdown):
            start = time.time()

            # caputure image from camera
            #self.camera.capture(self.stream,format='bgr',use_video_port=True)
            self.camera.capture_sequence(self.streams_generator(),use_video_port=True)

            for i in xrange(self.buffering_size):
                data = np.fromstring(self.streams[i].getvalue(),dtype=np.uint8)
                self.images[i] = cv2.imdecode(data,1)

            # turn the streams to array
            #self.current_image = self.streams.array
            end = time.time()
            delta = (end - start)
            print "capturing time: %f secs" % delta

            start = time.time()
            # do processing
            for image in self.images:
                processing(image)

            # save previous image

            # reinitialize the streams
            for stream in self.streams:
                stream.seek(0)
                stream.truncate()

            end = time.time()
            delta = (end - start)
            print "processing time: %f secs" % delta

        print "exiting"
        for stream in self.streams:
            stream.close()

View()
