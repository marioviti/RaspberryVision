import time
import signal
import cv2
import numpy as np

from Image_Processor import Image_Processor
from Tag_Detector import Tag_detection_experiment
import settings
import tag_recognition
import image_utils
import tests

import time

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

if __name__ == '__main__':
    """
    This program is designed to recognize Tags.
    """
    tag_detection_experiment = Tag_detection_experiment()
    tag_detection_experiment.setup()

    global RUNNING
    RUNNING = True
    signal.signal(signal.SIGINT, signal_handler_stop_running) #CTRL C
    signal.signal(signal.SIGTSTP, signal_handler_test) #CTRL Z

    tag_detection_experiment.start()
    print "hallowing camera to warm up"
    time.sleep(2)
    print "let's start!!!"
    tags_info = None
    while(RUNNING):
        time_d = time.time()
        newresults, tags_info = tag_detection_experiment.retrieve_post_results()
        tags_contours,tags_aligned,tags_ids,tags_distances,tags_rotations = tags_info
        if newresults and len(tags_contours)>0:
            message = 'distances: ' + `tags_distances` #+ '\n'
            message+= '\trotations: ' + `tags_rotations` # + '\n'
            message+= '\tids: ' + `tags_ids`
            message+= '\tdtime: ' + `tag_detection_experiment.tag_detector.perf_time`# + '\n'
            message+= '\tdtime_all: ' + `time_d-time.time()`# + '\n'
            tests.log(message,"")
        if TESTING:
            TESTING = False
            tags_contours,tags_aligned,tags_ids,tags_distances,tags_rotations = tags_info
            rgb_image = np.zeros((tag_detection_experiment.tag_detector.prec_frame.shape[0],tag_detection_experiment.tag_detector.prec_frame.shape[1],3),dtype=np.uint8)
            rgb_image[:,:,0] = tag_detection_experiment.tag_detector.prec_frame
            rgb_image[:,:,1] = rgb_image[:,:,0]
            rgb_image[:,:,2] = rgb_image[:,:,0]
            rgb_image = image_utils.draw_contours(rgb_image,tags_contours)
            image_utils.show_image(rgb_image)
            #image_utils.show_image(tag_detection_experiment.tag_detector.diff_frame)
            for tag_aligned in tags_aligned:
                image_utils.show_image(tag_aligned)
    tag_detection_experiment.shutdown()
    print "good bye"
