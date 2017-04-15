import cv2
import numpy as np
from numpy import linalg as lnag
import image_utils

#################################################################################
#                      TAG DETECION FOR RASPBERRY v.1.0                         #
#################################################################################
#                                                                               #
#       This is a collection of function used to detect identify and estimate   #
#       metrics from a tag.                                                     #
#       The tag is desribed in the settings file.                               #
#                                                                               #
#################################################################################

TAG_ID_ERROR = 99999

def distance_from_angluar_diameter(theta,D):
    """
        theta must be in radiants.
        theta is the angluar diameter which is proportional to the number of pixel
        occipied by the image.
        D is the actual known diameter of the object outscribed circle (approximation).
        result will be in the unit of D.
    """
    return np.tan(theta/2.)*2.*D

def deg_to_rad(alpha):
    """
        pi radians are 180 degrees.
    """
    return alpha*(np.pi/180.)

def calculate_angular_diameter(a_b,a_1_b_1,alpha):
    """
        It is the portion of viewing angle occupied by a circle occupying a
        portion of screen.

        This circle is an approximation of the projection of an object from the
        real world onto the screen.

        a_b is the vertical height of the image.
        a_1_b_1 is the diameter of the circle in pixels and
        the number of pixel occupied by the object.
        alpha is the angle at the aphex in degrees for the vertical
        axis(longitudinal) in deg, this degree can be found on the specs of the
        camera as fov (field of view).

        output angle is in degrees.
    """
    return (a_1_b_1/float(a_b)) * alpha

def estimate_distance(cnt,image_h,alpha=48,D=1):
    """
        image_h heitght of the image
        alpha longitudinal angle of the camera fov (usually 48 deg for picamera)
        D is the actual diameter of the circle outscribed the tag
    """
    centre, radius = min_circle(cnt) # the approximation of the object projection
    d = 2*radius
    theta = deg_to_rad(calculate_angular_diameter(image_h,d,alpha=alpha))
    return distance_from_angluar_diameter(theta,D)

@profile
def identify_tag(tag_image):
    """
        tag are 3x2 array,
        sample the center
    """
    y,x = tag_image.shape
    dx,dy = x/3,y/4
    dtau = 3
    id_tag = 0
    for i in range(2):
        for j in range(3):
            crdx, crdy = (1+i)*dx,(1+j)*dy
            sample = np.sum(tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau])/(16.*255.)
            tag_image[crdy-dtau:crdy+dtau,crdx-dtau:crdx+dtau] = 127
            # thresholding the noise
            if sample > 0.75:
                bit = 1
            elif sample < 0.25:
                bit = 0
            else:
                #notag
                return TAG_ID_ERROR
            id_tag += bit *2**(i+j*2)
    return id_tag

def threshold_tag(tag_image):
    """
        once a tag image is found binarize the input.
        as we model the tag signal as formant code composed
        by a rect function and 2 amplitudes (min gray,max gray)
        the optimal threshold maximizin the SNR is at the
        middle of the amplitudes.
    """
    thresh = (np.max(tag_image)+np.min(tag_image))/2.
    ret,thresh = cv2.threshold(tag_image,thresh,255,0)
    return thresh

# using kernprof -v -l for profiling
# @profile
# Total time: 0.00845 s on Pi3
def deskew(image,cnt,auto_size=False,maxWidth=100,maxHeight=100,bleed=5,bottom_off=75):
    """
        Square tags.
    """
    pts = cnt.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = np.float32)
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # the order now is
    # (tl, tr, br, bl) = rect

    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]],
        dtype = np.float32)

    # calculate the perspective transform matrix and warp
    M = cv2.getPerspectiveTransform(rect, dst)
    # attention opencv returns inveresd h and w!!!
    warp = cv2.warpPerspective(image, M, (maxWidth, bottom_off+maxHeight))      # 85.7
    warp_tag = warp[bleed:maxHeight-bleed,bleed:maxWidth-bleed]
    orient_tag = warp[maxHeight+bleed*3:,:]
    return warp_tag, orient_tag

# using kernprof -v -l for profiling
# @profile
# Total time: 0.160422 s
def detect_tags(gray_image, ar, D=1, sigma=0.3):
    tag_contours, edged = detect_tag_contours(gray_image, ar, sigma=sigma)      # 93.0
    warped_tags = []
    warped_orientations_tags = []
    tag_ids = []
    tag_distances = []
    for tag_contour in tag_contours:
        tag_distances += [ estimate_distance(tag_contour,gray_image.shape[1],D=D) ]
        warper_tag, warped_orientations_tag = deskew(gray_image,tag_contour)    # 5.0
        warped_orientations_tags += [ warped_orientations_tag ]
        warped_tags += [ warper_tag ]
    warped_tags = map(threshold_tag,warped_tags)
    warped_orientations_tags = map(threshold_tag,warped_orientations_tags)
    for warped_tag in warped_tags:
        tag_ids += [ identify_tag(warped_tag) ]
    return tag_contours, warped_tags, warped_orientations_tags, tag_ids, tag_distances

# using kernprof -v -l for profiling
# @profile
# Total time: 0.150379 s
def detect_tag_contours(gray_image, ar, sigma=0.3):
    # compute the median of the single channel pixel intensities
    v = np.median(gray_image)                                                   # 23.3
	# apply automatic Canny edge detection using the computed mean
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(gray_image, lower, upper)                                 # 20.0
    tag_contours = find_tag_contours(edged,ar)                                  # 56.6
    return tag_contours, edged

def is_tag_cnt(cnt_p, cnt_c, ar, sigma, eps):
    area_1 = cv2.contourArea(cnt_p)
    area_2 = cv2.contourArea(cnt_c)
    if area_1 > eps and area_2 > eps: # div by zero check
        area_ratio = area_1/float(area_2)
        return area_ratio <= ar+sigma and area_ratio >= ar-sigma
    return False

# using kernprof -v -l for profiling
# @profile
# Total time: 0.114152 s on Pi3
def find_tag_contours(edge_image, ar, sigma=0.3, eps=20, approx=cv2.CHAIN_APPROX_NONE):
    """
        CHAIN_APPROX_NONE fast result and better response for skewed tags.

        ar is the area_ratio of the tags markers (3 inscribed squares)
        eps and sigma are found experimentally:
            -sigma is the variance of the area_ratio.
            -eps is the minimum area in pixels for a contour to be considered.
    """
    contours, hierarchy = cv2.findContours(edge_image,cv2.RETR_TREE,approx)     # 27.6
    if hierarchy is None:
        return contours
    tag_contours = []
    N = len(contours)
    hierarchy = hierarchy[0]
    occour = np.zeros(N,np.dtype(np.bool))
    for curr in xrange(1,N):
        if not occour[curr]:
            # we do not approximate first contour
            # following depths will be checked
            # if all checks are clear than it will check for the parent
            # this saves up a lot of computation.
            child = hierarchy[curr][2]
            if child!=-1 and child<N-1:
                child_approxTop = approx_cnt(contours[child])
                if len(child_approxTop) == 4 and is_tag_cnt(contours[curr],contours[child],ar,sigma,eps):
                    next_curr = child+1
                    next_curr_approxTop = approx_cnt(contours[next_curr])
                    if len(next_curr_approxTop) == 4:
                        next_child = hierarchy[next_curr][2]
                        if next_child!=-1 and next_child<N-1:
                            next_child_approxTop = approx_cnt(contours[next_child])
                            if len(next_child_approxTop) == 4 and is_tag_cnt(contours[next_curr],contours[next_child],ar,sigma,eps):
                                curr_approxTop = approx_cnt(contours[curr])
                                if len(curr_approxTop) == 4:
                                    if not occour[curr]:
                                        occour[curr] = True
                                    if not occour[child]:
                                        occour[child] = True
                                    if not occour[next_curr]:
                                        occour[next_curr] = True
                                    if not occour[next_child]:
                                        occour[next_child] = True
                                        # save deepest contour
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

def min_circle(cnt):
     return cv2.minEnclosingCircle(cnt)

def rot_bounding_box(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    return box

def k_means(image,k=3):
    points = np.float32(image.reshape((-1,1)))
    term_crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, labels, centers = cv2.kmeans(points, k, term_crit, 10, 0)
    return ret, labels, centers

#def extend_square((tl, tr, br, bl), ext_factor, dir_='top'):
#    if dir_=='top':
#        tl1,tr1 = bl*(1-ext_factor)+tl*(ext_factor), br*(1-ext_factor)+tr*(ext_factor)
#        ret = np.array([ [tl1[0],tl1[1]],[tr1[0],tr1[1]],[tl[0],tr[1]],[tr[0],tr[1]] ])
#        return ret.reshape(4,2)
#    elif dir_=='bot':
#        return [tl, tr,tl*(1-ext_factor)+bl*(ext_factor),tr*(1-ext_factor)+br*(ext_factor)]
#    return None

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
