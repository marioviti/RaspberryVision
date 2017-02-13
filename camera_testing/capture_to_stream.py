import io
import time
import picamera

def capture_to_stream(stream):
    # Create an in-memory stream
    with picamera.PiCamera() as camera:
        camera.start_preview()
        # Camera warm-up time
        time.sleep(2)
        camera.capture(stream, 'jpeg')

my_stream = io.BytesIO()
print my_stream
