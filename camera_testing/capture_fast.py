import io
import cv2
import picamera
import numpy as np
import time

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 10
    #camera.start_preview()
    time.sleep(2)
    stream = io.BytesIO()
    key = 0
    while(key != ord("q")):
        camera.capture_sequence(stream,use_video_port=True)
        data = np.fromstring(stream.getvalue(),dtype=np.uint8)
        #turn the array into a cv2 image
        img = cv2.imdecode(data,1)
        cv2.imshow("image",image)
        key = cv2.waitKey(1) & 0xFF
        stream.seek(0)
        stream.truncate()
        # if the `q` key was pressed, break from the loop
