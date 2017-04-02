from Camera_Controller import Camera_Controller
import settings
import tag_recognition
import threading

class Tag_Identifier(threading.Thread):
    def __init__(self, tag_type = settings.DEFAULT_TYPE):
        super(Tag_Identifier, self).__init__()
        self.camera_controller = Camera_Controller()
        self.load_tag_settings(tag_type)
        self.initialize_results()
        self.initialize_locks()

    def load_tag_settings(self,tag_settings):
        self.tag_settings = settings.tags_settings[tag_settings]

    def initialize_results(self):
        # jollyfull threading problem reference
        self.available_chop_stick = True
        self.retrieve_chop_stick = False
        self.tag_orientations = None

    def initialize_locks(self):
        self.processing_result_lock = threading.Lock()

    def shutdown(self):
        self.running = False
        self.camera_controller.shutdown()

    def run(self):
        self.running = True
        self.camera_controller.start()
        while(self.running):
            # start the loop we'll ask for the camera controller for new data
            imgray = None
            with self.camera_controller.processing_buffer_lock:
                if self.camera_controller.processing_buffer != None:
                    imgray = tag_recognition.pre_processing_image(self.camera_controller.processing_buffer)
            if imgray!= None:
                contours_tag, tag_ids = tag_recognition.detecting_tag_ids(imgray,self.tag_settings['area_ratio'])
                with self.processing_result_lock:
                    # updating results
                    self.tag_ids = tag_ids
                    # setting flags for uptated results
                    self.available_chop_stick = True
                    self.pick_up_chop_stick = False
        self.shutdown()

    def retrieve_tag_id(self):
        with self.processing_result_lock:
            if self.pick_up_chop_stick:
                self.available_chop_stick = False
            self.pick_up_chop_stick = True
            # new results are available if self.available_chop_stick is true
            return self.available_chop_stick ,self.tag_id
