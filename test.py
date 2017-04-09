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
    ar = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]['area_ratio']
    tag_contours,warped_tags = tag_recognition.detect_tags(grey_image,ar)
    image = image_utils.draw_contours(image,tag_contours)
    for warped_tag in warped_tags:
        image_utils.show_image(warped_tag)
    image_utils.show_image(image)

test_opz = { 'tag_detection': test_tag_detection, }
if (len(sys.argv) == 1):
    print "defined tests are : "
    print test_opz.keys()
    sys.exit(0)
test = sys.argv[1]
arg = sys.argv[2]
test_opz[test](arg)
