# -*- coding: utf-8 -*-
"""
Created on Sun Nov  7 19:12:22 2021

@author: griessba
"""

import matlab.engine as me

import CAM_TVPT_110_image_geometry as igmLib

# name = me.find_matlab()
# if len(name)==0:
#     eng =me.start_matlab()
# else:
#     eng = me.connect_matlab()

eng = me.start_matlab()
eng.addpath('./matlabLib/', nargout=0)    


#centroiding test    
state = igmLib.test_centriod(eng)    

#IGM test
stateIGM = igmLib.test_cameraModelOptimization(eng)


eng.quit()