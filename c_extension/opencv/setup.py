#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup, Extension
import numpy as np

# include
cv2_includes = ['/usr/local/include/opencv', '/usr/local/include']
numpy_includes = [np.get_include()]
include_dirs = numpy_includes + cv2_includes

# linking

# '/usr/local/lib/libopencv_calib3d.so /usr/local/lib/libopencv_contrib.so
# /usr/local/lib/libopencv_core.so /usr/local/lib/libopencv_features2d.so
# /usr/local/lib/libopencv_flann.so /usr/local/lib/libopencv_gpu.so
# /usr/local/lib/libopencv_highgui.so /usr/local/lib/libopencv_imgproc.so
# /usr/local/lib/libopencv_legacy.so /usr/local/lib/libopencv_ml.so
# /usr/local/lib/libopencv_nonfree.so /usr/local/lib/libopencv_objdetect.so
# /usr/local/lib/libopencv_ocl.so /usr/local/lib/libopencv_photo.so
# /usr/local/lib/libopencv_stitching.so
# /usr/local/lib/libopencv_superres.so /usr/local/lib/libopencv_ts.a
# /usr/local/lib/libopencv_video.so /usr/local/lib/libopencv_videostab.so
# -lrt -lpthread -lm -ldl

library_dirs = ['/usr/local/lib/',]
libraries = ['opencv_core','opencv_imgproc','opencv_highgui']

ext_modules = [ Extension('cvtest',
    sources = ['cvtest.cpp'],
    library_dirs = library_dirs,
    libraries = libraries,) ]

setup(
        name = 'Cvtest',
        version = '1.0',
        include_dirs = include_dirs,
        ext_modules = ext_modules
     )
