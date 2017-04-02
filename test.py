from Tag_Recognition import tag_recognition
from Tag_Recognition import settings
from Tag_Recognition import image_utils

import numpy as np
import cv2
import sys

#@profile
def test_tag_detection(path):
    image = image_utils.read_image(path)
    grey_image = image_utils.convert_grey(image)
    tag_contours = tag_recognition.detecting_tag(grey_image,settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]['area_ratio'])
    image = image_utils.draw_contours(image,tag_contours)    
    image_utils.show_image(image)

test_opz = { 'tag_detection': test_tag_detection, }
if (len(sys.argv) == 1):
    print "defined tests are : "
    print test_opz.keys()
    sys.exit(0)
test = sys.argv[1]
arg = sys.argv[2]
test_opz[test](arg)
