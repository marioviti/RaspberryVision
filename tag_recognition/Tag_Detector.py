import cv2
import numpy as np
import time

from Image_Processor import Image_Processor
import settings
import tag_recognition
import image_utils
import tests

class Tag_Detector():
    def __init__(self, tag_settings = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]):
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.tag_results = None
        self.perf_time = 0
        self.image_processor = Image_Processor()
        self.image_processor.set_preprocessing_function(image_utils.convert_grey)
        self.image_processor.set_post_processing_function(self.tag_recognition_function)

    def tag_recognition_function(self,image):
        self.prec_frame = image
        self.perf_time = time.time()
        self.tag_results = tag_recognition.detect_tags(image,self.tag_settings[settings.AREA_RATIO_KEY],actual_side_size=self.tag_settings[settings.DIAGONAL_KEY])
        self.perf_time = time.time() - self.perf_time
        return self.tag_results

    def get_tag_data(self):
        newresults, tags_info = self.image_processor.retrieve_post_results()
        return newresults,tags_info

    def start(self):
        self.image_processor.start()

    def shutdown(self):
        self.image_processor.shutdown()
