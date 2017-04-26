
from tag_recognition import tag_recognition
from tag_recognition import settings
from tag_recognition import image_utils

import numpy as np
import cv2
import sys
import time

#@profile
def test_tag_detection(path):
    image = image_utils.read_image(path)
    grey_image = image_utils.convert_grey(image)
    ar = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]['area_ratio']
    tags_contours,tags_aligned,tags_ids,tags_distances,tags_rotations = tag_recognition.detect_tags(grey_image,ar)
    print 'ids: '
    print tags_ids
    image = image_utils.draw_contours(image,tags_contours)
    image_utils.show_image(image)
    for tag_aligned in tags_aligned:
        image_utils.show_image(tag_aligned)


test_opz = { 'tag_detection': test_tag_detection, }
if (len(sys.argv) == 1):
    print "defined tests are : "
    print test_opz.keys()
    sys.exit(0)
test = sys.argv[1]
arg = sys.argv[2]
print test
test_opz[test](arg)
