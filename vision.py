import time
import picamera
from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import tag_recognition

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera)
# allow the camera to warmup
time.sleep(2)
#camera.start_preview()
start = time.time()
i = 0
image = None
contours = None
tag_ids = None
ar = 2.205175
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    delta = time.time() - start
    print "capture and processing time %f" % delta
    start = time.time()
    image = frame.array
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    imgray,contours,tag_ids =tag_recognition.detect_tag(imgray,ar)
    rawCapture.seek(0)
    rawCapture.truncate()
    i+=1
    if i == 10:
        break

cnts_tag = []
for tag_id in tag_ids:
    cnts_tag += [contours[tag_id]]

cv2.drawContours(image, cnts_tag, -1, (255,0,0), 3)
for c in cnts_tag:
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    cv2.circle(image, extLeft, 8, (0, 0, 255), -1)
    cv2.circle(image, extRight, 8, (0, 255, 0), -1)


cv2.imshow('image',image)
cv2.waitKey(0) # press any key
rawCapture.close()
cv2.destroyAllWindows()
