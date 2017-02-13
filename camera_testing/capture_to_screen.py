import time
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(2)
#camera.start_preview()
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    cv2.imshow("image",image)
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    key = cv2.waitKey(0) & 0xFF
    if key == ord("q"):
        break

cv2.destroyAllWindows()
