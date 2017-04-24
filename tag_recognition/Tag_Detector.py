import cv2
import numpy as np
import time

from Image_Processor import Image_Processor
import settings
import tag_recognition
import image_utils
import tests

class Tag_Detector():
    def __init__(self,tag_settings):
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.diff_frame = None
        self.count = 0
        self.tag_results = None
        self.perf_time = None

    def get_tags_info(self,image):
        if self.diff_frame is None:
            self.prec_frame = image
            self.perf_time = time.time()
            self.tag_results = tag_recognition.detect_tags(image,self.tag_settings[settings.AREA_RATIO_KEY],actual_side_size=self.tag_settings[settings.DIAGONAL_KEY])
            self.perf_time = time.time() - self.perf_time
            #tests.log('time',`self.perf_time`)
        elif self.count == 0:
            self.diff_frame = image - self.prec_frame
            self.prec_frame = image
            self.count = 1
        elif self.count == 1:
            self.count = 0
            self.prec_frame = image
            self.perf_time = time.time()
            self.tag_results = tag_recognition.detect_tags(image,self.tag_settings[settings.AREA_RATIO_KEY],actual_side_size=self.tag_settings[settings.DIAGONAL_KEY])
            self.perf_time = time.time() - self.perf_time
        return self.tag_results

class Tag_detection_experiment():
    def __init__(self,settings=settings,tag_type=settings.DOUBLE_SQUARE_TYPE):
        self.settings = settings
        self.tag_type = tag_type
        self.tag_detector = None
        self.image_processor = None

    def setup(self):
        self.tag_detector = Tag_Detector(self.settings.tags_settings[self.tag_type])
        self.image_processor = Image_Processor()
        self.image_processor.set_preprocessing_function(image_utils.convert_grey)
        self.image_processor.set_post_processing_function(self.tag_detector.get_tags_info)

    def start(self):
        self.image_processor.start()

    def shutdown(self):
        self.image_processor.shutdown()

    def retrieve_post_results(self):
        newresults, tags_info = self.image_processor.retrieve_post_results()
        return newresults,tags_info