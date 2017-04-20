
from Tag_Recognition import tag_recognition
from Tag_Recognition import settings
from Tag_Recognition import image_utils

import numpy as np
import cv2
import sys
import time

#@profile
def test_tag_detection(path):
    image = image_utils.read_image(path)
    grey_image = image_utils.convert_grey(image)
    ar = settings.tags_settings[settings.DOUBLE_SQUARE_TYPE]['area_ratio']
    tag_contours, warped_tags, warped_orientations_tags, tag_ids, tag_distances, rotations = tag_recognition.detect_tags(grey_image,ar)
    print 'ids: '
    print tag_ids
    print 'rotations:'
    print rotations
    print 'distances: '
    print tag_distances
    image = image_utils.draw_contours(image,tag_contours)
    for warped_tag in warped_tags:
        image_utils.show_image(warped_tag)
    for warped_orientations_tag in warped_orientations_tags:
        image_utils.show_image(warped_orientations_tag)
    image_utils.show_image(image)

test_opz = { 'tag_detection': test_tag_detection, }
if (len(sys.argv) == 1):
    print "defined tests are : "
    print test_opz.keys()
    sys.exit(0)
test = sys.argv[1]
arg = sys.argv[2]
print test
test_opz[test](arg)
