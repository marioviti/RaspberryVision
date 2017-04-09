import time
import signal
import cv2
import numpy as np

from Image_Processor import Image_Processor
import settings
import tag_recognition
import image_utils

RUNNING = True
TESTING = False

def signal_handler_stop_running(signal, frame):
    print signal
    print "signal_handler_stop_running"
    global RUNNING
    RUNNING = False

def signal_handler_test(signal, frame):
    print "signal_handler_test"
    global TESTING
    TESTING = True

framecount = 0
def count_frames(image):
    global framecount
    framecount += 1
    print framecount
    return image

class Tag_Detector():
    def __init__(self,tag_settings):
        self.tag_settings = tag_settings
        self.prec_frame = None
        self.diff_frame = None
        self.count = 0
        self.tag_contours = None

    def detect_tag(self,image):
        if self.diff_frame is None:
            self.prec_frame = image
            self.tag_contours = tag_recognition.detect_tag_contours(image,self.tag_settings[settings.AREA_RATIO_KEY])
        elif self.count == 0:
            self.diff_frame = image - self.prec_frame
            self.prec_frame = image
            self.count = 1
        elif self.count == 1:
            self.count = 0
            self.prec_frame = image
            self.tag_contours = tag_recognition.detect_tag_contours(image,self.tag_settings[settings.AREA_RATIO_KEY])
        return self.tag_contours

if __name__ == '__main__':
    """
    This program is designed to recognize Tags.
    """
    tag_detector = Tag_Detector(settings.tags_settings[settings.DOUBLE_SQUARE_TYPE])

    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, signal_handler_stop_running)
    signal.signal(signal.SIGTSTP, signal_handler_test)
    image_processor = Image_Processor()
    image_processor.set_preprocessing_function(image_utils.convert_grey)
    image_processor.set_post_processing_function(tag_detector.detect_tag)
    image_processor.start()
    print "hallowing camera to warm up"
    time.sleep(4)
    print "let's start!!!"
    countours = None
    while(RUNNING):
        newresults, countours = image_processor.retrieve_post_results()
        if TESTING:
            TESTING = False
            rgb_image = np.zeros((tag_detector.prec_frame.shape[0],tag_detector.prec_frame.shape[1],3),dtype=np.uint8)
            rgb_image[:,:,0] = tag_detector.prec_frame
            rgb_image[:,:,1] = rgb_image[:,:,0]
            rgb_image[:,:,2] = rgb_image[:,:,0]
            rgb_image = image_utils.draw_contours(rgb_image,countours)
            image_utils.show_image(rgb_image)
    image_processor.shutdown()
    print "good bye"
