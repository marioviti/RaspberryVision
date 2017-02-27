import io
import time
import threading
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

import signal
import sys

def signal_handler(signal, frame):
    print "CTRL-C"
    global shutdown
    shutdown = True
    fetcher.terminated = True

lock = threading.Lock()
shutdown = False

class Fetcher(threading.Thread):
    def __init__(self,image_size=(680,480),fr=5):
        super(Fetcher, self).__init__()
        self.good_to_capture = threading.Event()
        self.good_to_decode = threading.Event()
        self.terminated = False
        self.stream = None
        self.camera = None
        self.initialize_status(image_size,fr)
        self.start()

    def initialize_status(self,*args):
        self.camera = picamera.PiCamera()
        self.camera.resolution = args[0]
        self.camera.framerate = args[1]
        self.stream = io.BytesIO()

    def generate_stream(self):
        """
            yielding the generators for our streams
        """
        # here we should check if we're good_to_capture
        while not self.terminated:
            if self.good_to_capture.wait(1):
                print "fetcher thread"
                #self.stream.truncate() # leave buffer as it is with data coming from the camera
                self.stream.seek(0) # reset the beginning to 0, to rewrite in existing memory
                yield self.stream
                self.good_to_decode.set()
                self.good_to_capture.clear()

    def run(self):
        while not self.terminated:
            if self.good_to_capture.wait(1):
                self.camera.capture_sequence(self.generate_stream(),use_video_port=True)


signal.signal(signal.SIGINT, signal_handler)
fetcher = Fetcher()
fetcher.good_to_capture.set()

current_image = None
while(not shutdown):
    start = time.time()
    if fetcher.good_to_decode.wait(1):
        fetcher.good_to_decode.clear()
        start = time.time()
        print fetcher.stream.tell()
        data = np.fromstring(fetcher.stream.getvalue(),dtype=np.uint8)
        fetcher.good_to_capture.set()
        current_image = cv2.imdecode(data,1)
        processed_image = cv2.Canny(current_image,100,200)
    end = time.time()
    delta = (end - start)
    print "loop_time time: %f secs" % delta
