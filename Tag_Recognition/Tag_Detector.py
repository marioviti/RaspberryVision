from Camera_Controller import Camera_Controller
import Settings
import tag_recognition

class Processor(threading.Thread):
    """
        Taf_Detector can work on demand or as a demon:
        continiously calculating the desired effect.
    """
    def __init__(self):
        super(Processor, self).__init__()
        self.camera_controller = Camera_Controller()

        # the processing to be applied to the processing_buffer
        self.processing = tag_recognition.processing_image
        # the processing to be applied to the results
        # indipendently of the processing_buffer
        self.post_processing = tag_recognition.detecting_tag
        self.processing_results = None
        self.post_processing_results = None

        # set _running flag for gracious termination
        self._running = True

    def shutdown(self):
        self._running = False

    def run(self):
        while(self._running):
            with self.camera_controller.processoing_buffer_lock:
                if self.camera_controller.processing_buffer != None:
                    self.processing_results = self.processing(self.camera_controller.processing_buffer)
            self.post_processing_results = self.post_processing(self.processing_results)

    def serve_post_processing_results(self):
        with self.camera_controller.processoing_buffer_lock:
            if self.camera_controller.processing_buffer != None:
                self.processing_results = self.processing(self.camera_controller.processing_buffer)
        return self.post_processing_results = self.post_processing(self.processing_results)
