import io
import time
import threading
import picamera
import numpy as np
import cv2

# Create a pool of image processors
done = False
lock = None
pool = []
idx = 0

class ImageProcessor(threading.Thread):
    def __init__(self):
        global idx
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.image = None
        self.id = idx
        idx += 1
        self.start()

    def run(self):
        # This method runs in a separate thread
        global done
        global pool
        global lock
        while not self.terminated:
            # Wait for an image to be written to the stream
            print 'thread %d waiting' % self.id
            if self.event.wait(1):
                print 'thread %d event signalled' % self.id
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    # self.image = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    # Set done to True if you want the script to terminate
                    # at some point
                    # print self.image.shape
                    key = cv2.waitKey(0) & 0xFF
                    if key == ord('q'):
                        done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        pool.append(self)

def streams():
    global done
    global pool
    global lock
    while not done:
        with lock:
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            yield processor.stream
            processor.event.set()
        else:
            print 'streams'
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)

with picamera.PiCamera() as camera:
    global lock
    lock = threading.Lock()
    pool = [ImageProcessor() for i in range(4)]
    camera.resolution = (640, 480)
    camera.framerate = 10
    camera.start_preview()
    time.sleep(2)
    camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
    global done
    global pool
    global lock
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
