import numpy as np
import cv2

TRIANGLE_TYPE = 0
SQUARE_TYPE = 1

def estimate_Affine(src,dst, tag_type=TRIANGLE_TYPE):
    if tag_type == TRIANGLE_TYPE:
        src = add_center_triangle(src_tag_edges)
        dst = add_center_triangle(dst_tag_edges)
    estimated_M = cv2.getPerspectiveTransform(src, dst)
    return estimated_M

triangle = [tuple((10,10)),tuple((400,200)),tuple((10,400))]
square = [tuple((10,10)),tuple((10,400)),tuple((400,400)),tuple((400,10))]

def draw_triangle(image,a,b,c,d):
    cv2.line(image,a,b,(255,0,0),5)
    cv2.line(image,b,c,(255,0,0),5)
    cv2.line(image,a,c,(255,0,0),5)
    cv2.circle(image, d, 5, (255, 0, 0), -1)

def draw_square(image,a,b,c,d):
    cv2.line(image,a,b,(255,0,0),5)
    cv2.line(image,b,c,(255,0,0),5)
    cv2.line(image,c,d,(255,0,0),5)
    cv2.line(image,d,a,(255,0,0),10)

def add_center_to_triangle(a,b,c):
    ox = int((a[0]+b[0]+c[0])/3.)
    oy = int((a[1]+b[1]+c[1])/3.)
    return [a,b,c,tuple((ox,oy))]

def add_center_triangle(t):
    ox = (t[0][0]+t[1][0]+t[2][0])/3.
    oy = (t[0][1]+t[1][1]+t[2][1])/3.
    return np.vstack((t,[ox,oy]))

triangle_c = add_center_to_triangle(*triangle)
image = np.zeros((480,640))
#draw_square(image,*square)
draw_triangle(image,*triangle_c)
Mtot = np.float32([[0.4,1.,0],[1.,0.,0],[0.,0.,1.]])
M = Mtot[:2]

n = len(triangle_c)
#n = len(square)
src = np.zeros((n,2), dtype = "float32")
for i in range(n):
    src[i,0],src[i,1] = triangle_c[i][0],triangle_c[i][1]

dst = np.zeros((n,2), dtype = "float32")
for i in range(n):
    hv = np.array([triangle_c[i][0],triangle_c[i][1],1])
    vertex_i = Mtot.dot(hv)
    dst[i,0],dst[i,1] = vertex_i[0],vertex_i[1]

estimatedM = cv2.getPerspectiveTransform(src, dst)

dstImage = cv2.warpAffine(image,Mtot[:2],(image.shape[1],image.shape[0]))
dstImageEstimaged = cv2.warpAffine(image,estimatedM[:2],(image.shape[1],image.shape[0]))

"""
print src
print dst
print Mtot
print estimatedM
"""
print src.shape
print add_center_triangle(src).shape

cv2.imshow('image',image)
cv2.waitKey(0) # press any key
cv2.imshow('image',dstImage)
print dstImage.shape
cv2.waitKey(0) # press any key
cv2.imshow('image',dstImageEstimaged)
print dstImageEstimaged.shape
cv2.waitKey(0) # press any key
cv2.destroyAllWindows()
