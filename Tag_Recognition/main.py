import time
import Camera_Controller
import tag_recognition
import signal

RUNNING = True

def signal_handler(signal, frame):
    print "CTRL-C"
    global RUNNING
    RUNNING = False

if __name__ == '__main__':
    """
    This program is designed to recognize Tags.
    """
    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, signal_handler)
    camera_controller = Camera_Controller.Camera_Controller()
    camera_controller.start()
    results = None
    image = None
    while(RUNNING):
        if camera_controller.processing_buffer!=None:
            with camera_controller.processing_buffer_lock:
                print "processing"
                imgray = tag_recognition.pre_processing_image(camera_controller.processing_buffer)
            contours, tag_ids = tag_recognition.detecting_tag(imgray)
    camera_controller.shutdown()
