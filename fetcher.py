import io
import time
import threading
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2

lock = threading.Lock()
shutdown = False

class Fetcher(threading.Thread):
    def __init__(self,image_size=(680,480),fr=10):
        super(Fetcher, self).__init__()
        self.good_to_capture = threading.Event()
        self.good_to_process = threading.Event()
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
                self.good_to_process.set()
                self.good_to_capture.clear()

    def run(self):
        while not self.terminated:
            if self.good_to_capture.wait(1):
                self.camera.capture_sequence(self.generate_stream(),use_video_port=True)

class Shower(threading.Thread):
    def __init__(self):
        super(Shower, self).__init__()
        self.good_to_show = threading.Event()
        self.good_to_process = threading.Event()
        self.good_to_process.set()
        self.terminated = False
        self.image = None
        self.key = None
        self.start()

    def run(self):
        while not self.terminated:
            if self.good_to_show.wait(1):
                self.key = show(self.image)
                self.good_to_show.clear()
                self.good_to_process.set()

def show(image):
    cv2.imshow("image",image)
    return cv2.waitKey(1) & 0xFF

fetcher = Fetcher()
shower = Shower()
fetcher.good_to_capture.set()
data = None
while(not shutdown and not shower.key == ord('q')):
    if fetcher.good_to_process.wait(1):
        fetcher.good_to_process.clear()
        start = time.time()
        print fetcher.stream.tell()
        data = np.fromstring(fetcher.stream.getvalue(),dtype=np.uint8)
        fetcher.good_to_capture.set()
        if shower.good_to_process.wait(1):
            shower.good_to_process.clear()
            shower.image = cv2.imdecode(data,1)
            if not shower.image == None:
                shower.good_to_show.set()
        end = time.time()
        delta = (end - start)
        print "main thread decoding time: %f secs" % delta

fetcher.terminated = True
shower.terminated = True
