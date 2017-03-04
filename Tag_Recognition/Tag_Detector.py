from Camera_Controller import Camera_Controller
import Settings
import tag_recognition
import signal
import threading

global running
running = True

def signal_handler(signal, frame):
    print "CTRL-C"
    global running
    running = True

class Tag_Detector(threading.Thread):
    """
        Taf_Detector can work on demand or as a demon:
        continiously calculating the desired effect.
    """
    def __init__(self):
        super(Tag_Detector, self).__init__()
        self.camera_controller = Camera_Controller()

        # the processing to be applied to the processing_buffer
        self.processing = tag_recognition.processing_image
        # the processing to be applied to the results
        # indipendently of the processing_buffer
        self.post_processing = tag_recognition.detecting_tag
        self.processing_results = None
        self.post_processing_results = None

    def shutdown(self):
        global running
        running = False

    def run(self):
        signal.signal(signal.SIGINT, signal_handler)
        self.camera_controller.start()
        global running
        while(running):
            with self.camera_controller.processoing_buffer_lock:
                print "hangling the buffer"
                if self.camera_controller.processing_buffer != None:
                    self.processing_results = self.processing(self.camera_controller.processing_buffer)
            self.post_processing_results = self.post_processing(self.processing_results)
        self.camera_controller.shutdown()

    def serve_post_processing_results(self):
        with self.camera_controller.processoing_buffer_lock:
            if self.camera_controller.processing_buffer != None:
                self.processing_results = self.processing(self.camera_controller.processing_buffer)
        self.post_processing_results = self.post_processing(self.processing_results)
        return self.post_processing_results
