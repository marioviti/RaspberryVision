#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup, Extension
import numpy as np

cv2_includes = [ '/home/mario/anaconda2/pkgs/opencv-3.1.0-np111py27_1/include','/home/mario/opencv-3.2.0/modules/highgui/include','/home/mario/opencv-3.2.0/modules/core/include','/usr/local/include/opencv2/contrib','/usr/local/include/opencv2/core','/usr/local/include/opencv2/highgui','/usr/local/include/opencv2/imgproc','/usr/local/include']
numpy_includes = np.get_include()

include_dirs = [numpy_includes] + cv2_includes

ext_modules = [ Extension('cvtest', sources = ['cvtest.cpp']) ]

setup(
        name = 'Cvtest',
        version = '1.0',
        include_dirs = include_dirs,
        ext_modules = ext_modules
     )
