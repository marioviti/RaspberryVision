import cv2
import numpy as np
from numpy import linalg as lnag

def pre_processing_image(image):
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return imgray

def countour_extreme_points(contour):
    extLeft,extRight,extTop,extBottom = None,None,None,None
    extLeft = np.array(contour[contour[:, :, 0].argmin()][0])
    extRight = np.array(contour[contour[:, :, 0].argmax()][0])
    extTop = np.array(contour[contour[:, :, 1].argmin()][0])
    extBottom = np.array(contour[contour[:, :, 1].argmax()][0])
    return extLeft,extRight,extTop,extBottom

def triangle_orientation(L,R,T,B):
    """
        0: left
        1: right
    """
    collisions = np.array([lnag.norm(T-R),lnag.norm(B-R),lnag.norm(T-L),lnag.norm(B-L)])
    collision = np.argmin(collisions)
    if collision == 0 or collision == 1:
        return 0
    else:
        return 1

def countours_extreme_points(contours):
    extsLeft,extsRight,extsTop,extsBottom = [],[],[],[]
    for c in contours:
        extLeft,extRight,extTop,extBottom = countour_extreme_points(c)
        extsLeft += [ extLeft ]
        extsRight += [ extRight ]
        extsTop += [ extTop ]
        extsBottom += [ extBottom ]
    return extsLeft,extsRight,extsTop,extsBottom


def detecting_tag(imgray, ar, sigma=1.0, eps=100):
    """
        eps and sigma are found experimentally
        post ptocessing
    """
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    tag_ids = []
    if hierarchy == None:
        return contours, tag_ids
    hierarchy = hierarchy[0]
    for curr in xrange(1,len(contours)):
        child = hierarchy[curr][2]
        if child!=-1:
            area_1 = cv2.contourArea(contours[curr])
            area_2 = cv2.contourArea(contours[child])
            if area_2!=0:
                area_ratio = area_1/area_2
                if area_ratio <= ar+2*sigma and area_ratio >= ar-2*sigma and area_1>eps:
                    tag_ids += [curr,child]
    tag_ids = np.unique(tag_ids)
    return contours, tag_ids
