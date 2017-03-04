import cv2
import numpy as np

tag_template = {
"""
It's a square
"""
    "vertices" : [(0,0),(1,0),(0,1),(1,1)],
}

tags_descriptors = { "vertices" : [] }

def pre_processing_image(image):
    """
        this operations block the image acquisition
    """
    imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return imgray

def detecting_tag(imgray, ar=2.205175, sigma=1.0, eps=100):
    """
        post ptocessing
    """
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    tag_ids = []
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

def detect_tag(imgray,ar,sigma=1.0,eps=100):
    """
    ar area ratio.
    sigma theorized noise size on areas distortions
    eps min area with same ar
    """
    #cv2.normalize(imgray, imgray, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    tag_ids = []
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
    return imgray, contours, tag_ids

"""image = cv2.imread('tags6.png')
image[:,:,2] = 0
image[:,:,0] = 0
imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

ar = 2.205175
image,contours,tag_ids = detect_tag(imgray,ar)

contours_tag = []
for tag_id in tag_ids:
    contours_tag += [contours[tag_id]]
cv2.drawContours(image, contours_tag, -1, (255,0,0), 3)

cv2.imshow('image',image)
cv2.waitKey(0) # press any key
cv2.destroyAllWindows()"""
