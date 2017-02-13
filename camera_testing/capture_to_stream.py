import io
import time
import picamera
import cv2
import numpy as np

def capture_to_stream(stream = io.BytesIO()):
    # Create an in-memory stream
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(stream, 'jpeg')
