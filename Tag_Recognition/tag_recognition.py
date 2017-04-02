import cv2
import numpy as np
from numpy import linalg as lnag
#from sklearn.cluster import KMeans

@profile
def detecting_tag(gray_image, ar, sigma=0.3):
    # compute the mean of the single channel pixel intensities
    v = np.mean(gray_image)
	# apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(gray_image, lower, upper)

    tag_contours = find_tag_contours(edged,ar)
    tag_boxes = map(rot_bounding_box,tag_contours)
    return tag_boxes

def is_tag_cnt(cnt_p, cnt_c, ar, sigma, eps):
    area_1 = cv2.contourArea(cnt_p)
    area_2 = cv2.contourArea(cnt_c)
    if area_1>eps and area_2>eps:
        area_ratio = area_1/area_2
        if area_ratio <= ar+sigma and area_ratio >= ar-sigma:
            return True
    return False

@profile
def find_tag_contours(image, ar, sigma=0.3, eps=20):
    """
        eps and sigma are found experimentally
        post ptocessing
    """
    contours, hierarchy = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return contours
    tag_contours = []
    N = len(contours)
    hierarchy = hierarchy[0]
    occour = np.zeros(N,np.dtype(np.bool))
    for curr in xrange(1,N):
        if (not occour[curr]):
            child = hierarchy[curr][2]
            if child!=-1 and is_tag_cnt(contours[curr],contours[child],ar,sigma,eps):
                next_curr = child+1
                next_child = hierarchy[next_curr][2]
                if next_child!=-1 and is_tag_cnt(contours[next_curr],contours[next_child],ar,sigma,eps):
                    if not occour[curr]:
                        occour[curr] = True
                        tag_contours += [contours[curr]]
                    if not occour[child]:
                        occour[child] = True
                    if not occour[next_curr]:
                        occour[next_curr] = True
                    if not occour[next_child]:
                        occour[next_child] = True
                        tag_contours += [contours[next_child]]
    return tag_contours

def pre_processing_image(image):
    gray_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return gray_image

def bounding_box(cnt):
    return cv2.boundingRect(cnt)

def rot_bounding_box(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    return box

##ef countour_extreme_points(contour):
##    extLeft,extRight,extTop,extBottom = None,None,None,None
##    extLeft = np.array(contour[contour[:, :, 0].argmin()][0])
##    extRight = np.array(contour[contour[:, :, 0].argmax()][0])
##    extTop = np.array(contour[contour[:, :, 1].argmin()][0])
##    extBottom = np.array(contour[contour[:, :, 1].argmax()][0])
##    return extLeft,extRight,extTop,extBottom


##ef triangle_orientation(L,R,T,B):
##    """
##        0: left
##        1: right
##    """
##    collisions = np.array([lnag.norm(T-R),lnag.norm(B-R),lnag.norm(T-L),lnag.norm(B-L)])
##    collision = np.argmin(collisions)
##    if collision == 0 or collision == 1:
##        return 0
##    else:
##        return 1

##ef countours_extreme_points(contours):
##    extsLeft,extsRight,extsTop,extsBottom = [],[],[],[]
##    for c in contours:
##        extLeft,extRight,extTop,extBottom = countour_extreme_points(c)
##        extsLeft += [ extLeft ]
##        extsRight += [ extRight ]
##        extsTop += [ extTop ]
##        extsBottom += [ extBottom ]
##    return extsLeft,extsRight,extsTop,extsBottom

##ef estimate_Affine(src,dst, tag_type=TRIANGLE_TYPE):
##    if tag_type == TRIANGLE_TYPE:
##        src = add_center_triangle(src_tag_edges)
##        dst = add_center_triangle(dst_tag_edges)
##    estimated_M = cv2.getPerspectiveTransform(src, dst)
##    return estimated_M

##ef add_center_triangle(t):
##    ox = (t[0][0]+t[1][0]+t[2][0])/3.
##    oy = (t[0][1]+t[1][1]+t[2][1])/3.
##    return np.vstack((t,[ox,oy]))

##ef k_means(image,k=3):
##    points = np.float32(image.reshape((-1,1)))
##    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
##    ret, labels, centers = cv2.kmeans(points, k, term_crit, 10, 0)
##    return ret, labels, centers


#show_image(edged)

# use k means to adjust scene luminosity
#resized = cv2.resize(gray_image,None,fx=0.125,fy=0.125,interpolation=cv2.INTER_LINEAR)
#k = 3
## opencv way

##points = np.float32(gray_image.reshape((-1,1)))
#term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
#ret, labels, centers = cv2.kmeans(points, k, term_crit, 10, 0)

# opencv way

# sklearn way
#resized = resized.reshape((resized.shape[0] * resized.shape[1],1))
#clt = KMeans(n_clusters =k)
#clt.fit(resized)
#centers = clt.cluster_centers_
## sklearn way
#tag_contours = []
#for center in centers:
#    # search tag in each image
#    ret,thresh = cv2.threshold(gray_image,center,255,0)
#    tag_contours += find_tag_contours(thresh,ar)
