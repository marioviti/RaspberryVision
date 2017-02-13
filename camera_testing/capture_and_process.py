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
image_lock = None

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
        global image_lock
        while not self.terminated:
            # Wait for an image to be written to the stream
            print 'thread %d waiting' % self.id
            if self.event.wait(1):
                print 'thread %d event signalled' % self.id
                try:
                    self.stream.seek(0)
                    # Read the image and do some processing on it
                    data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                    self.image = cv2.imdecode(data, 1)
                    with image_lock: ## is not thread safe!!!!!
                        cv2.imshow('image',self.image)
                        print 'image shown'
                    # Set done to True if you want the script to terminate
                    # at some point
                    # print self.image.shape
                    #key = cv2.waitKey(0) & 0xFF
                    #if key == ord('q'):
                    #    done=True
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        print 'thread %d back on the pool' % self.id
                        pool.append(self)
        if self.terminated:
            cv2.destroyAllWindows()

def streams():
    global done
    global pool
    global lock
    processor = None
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
            print 'waiting for threads'
            # When the pool is starved, wait a while for it to refill
            time.sleep(0.1)

with picamera.PiCamera() as camera:
    global lock
    global image_lock
    lock = threading.Lock()
    image_lock = threading.Lock()
    pool = [ImageProcessor() for i in range(2)]
    camera.resolution = (640, 480)
    camera.framerate = 10
    #camera.start_preview()
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
