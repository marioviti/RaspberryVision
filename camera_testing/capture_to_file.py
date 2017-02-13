import time
import picamera

def capture_to_file(filename,resolution=(1024, 768)):
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(filename)

capture_to_file('test_capture_to_file.jpg')
