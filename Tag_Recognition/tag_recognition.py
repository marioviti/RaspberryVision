import cv2
import numpy as np
from numpy import linalg as lnag
import image_utils
#from sklearn.cluster import KMeans

def identify_tag(tag_image):
    return None

def threshold_tag(tag_image):
    max_v = max(np.max(tag_image),255)
    min_v = np.min(tag_image)
    thresh = (max_v+min_v)/2.
    ret,thresh = cv2.threshold(tag_image,thresh,255,0)
    return thresh

@profile
def deskew(image,cnt,auto_size=False,h_size=100,w_size=100,bleed=5):
    """
    Square tags
    """
    pts = cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = np.float32)
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # now that we have our rectangle of points, let's compute
    # the width of our new image
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

    # ...and now for the height of our new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

    # take the maximum of the width and height values to reach
    # our final dimensions
    if auto_size:
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
    else:
        maxWidth = w_size
        maxHeight = h_size

    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]], dtype = np.float32)

    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warp[bleed:w_size-bleed,bleed:h_size-bleed]

def detect_tags(gray_image, ar, sigma=0.3):
    tag_contours, edged = detect_tag_contours(gray_image, ar, sigma=0.3)
    warped_tags = []
    tag_ids = []
    for tag_contour in tag_contours:
        warped_tags += [ deskew(gray_image,tag_contour) ]
    warped_tags = map(threshold_tag,warped_tags)
    for warped_tag in warped_tags:
        tag_ids += [ identify_tag(warped_tag) ]
    return tag_contours, warped_tags, tag_ids

def detect_tag_contours(gray_image, ar, sigma=0.3):
    # compute the mean of the single channel pixel intensities
    v = np.median(gray_image)
	# apply automatic Canny edge detection using the computed mean
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(gray_image, lower, upper)
    tag_contours = find_tag_contours(edged,ar)
    tag_boxes = map(rot_bounding_box,tag_contours)
    return tag_contours, edged

def is_tag_cnt(cnt_p, cnt_c, ar, sigma, eps):
    area_1 = cv2.contourArea(cnt_p)
    area_2 = cv2.contourArea(cnt_c)
    area_ratio = area_1/float(area_2)
    return area_1>eps and area_2>eps and area_ratio <= ar+sigma and area_ratio >= ar-sigma

def find_tag_contours(image, ar, sigma=0.3, eps=20, approx = cv2.CHAIN_APPROX_NONE):
    """
        CHAIN_APPROX_NONE fast result and better response for skewed tags.

        eps and sigma are found experimentally:
            -sigma is the variance of the area_ratio.
            -eps is the minimum area in pixel for a contour to be considered.
    """
    contours, hierarchy = cv2.findContours(image,cv2.RETR_TREE,approx)
    if hierarchy is None:
        return contours
    tag_contours = []
    N = len(contours)
    hierarchy = hierarchy[0]
    occour = np.zeros(N,np.dtype(np.bool))
    for curr in xrange(1,N):
        if not occour[curr]:
            curr_approxTop = approx_cnt(contours[curr])
            if len(curr_approxTop) == 4:
                child = hierarchy[curr][2]
                child_approxTop = approx_cnt(contours[child])
                if child!=-1 and child<N-1 and len(child_approxTop) == 4 and is_tag_cnt(contours[curr],contours[child],ar,sigma,eps):
                    next_curr = child+1
                    next_curr_approxTop = approx_cnt(contours[next_curr])
                    if len(next_curr_approxTop) == 4:
                        next_child = hierarchy[next_curr][2]
                        next_child_approxTop = approx_cnt(contours[next_child])
                        if next_child!=-1 and next_child<N-1 and len(next_child_approxTop) == 4 and is_tag_cnt(contours[next_curr],contours[next_child],ar,sigma,eps):
                            if not occour[curr]:
                                occour[curr] = True
                                #tag_contours += [curr_approxTop]
                            if not occour[child]:
                                occour[child] = True
                            if not occour[next_curr]:
                                occour[next_curr] = True
                            if not occour[next_child]:
                                occour[next_child] = True
                                tag_contours += [next_child_approxTop]
    return tag_contours

def approx_cnt(cnt):
    peri = cv2.arcLength(cnt, True)
    approxTop = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    return approxTop

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



#def countour_extreme_points(contour):
#    extLeft,extRight,extTop,extBottom = None,None,None,None
#    extLeft = np.array(contour[contour[:, :, 0].argmin()][0])
#    extRight = np.array(contour[contour[:, :, 0].argmax()][0])
#    extTop = np.array(contour[contour[:, :, 1].argmin()][0])
#    extBottom = np.array(contour[contour[:, :, 1].argmax()][0])
#    return np.array([extLeft,extRight,extTop,extBottom])


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
