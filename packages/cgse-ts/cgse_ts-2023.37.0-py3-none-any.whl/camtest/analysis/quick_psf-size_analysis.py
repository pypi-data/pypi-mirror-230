# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 15:49:55 2021

@author: pert_mr
"""

import astropy.io.fits as pyfits
import numpy as np

import camtest.analysis.CAM_TVPT_010_best_focus_analysis as bestfocus_library
import camtest.analysis.convenience as cv

# TO BE UPDATED with the real workdir including the data
workdir = 'C:/Users/pert_mr/Documents/0_Projects/0_PLATO/Calibration-Integration/PCOT/BestFocus/CSL_data_test/'

#num_layers = 4
obsid = int(input("Which obsid to open?"))
fits_number = int(input("Which fitsnumber to open?"))

filename = cv.fileSelect([f'00{obsid}_', f'0{fits_number}_','cube','fits'],location=workdir)
hduc = pyfits.open(workdir+filename[0], ignore_missing_simple=True)

data_cube = hduc[2].data
data_cube = np.delete(data_cube,0,0)    #needed to remove the 1st saturated layer

data_layer = data_cube[0]

#plt.imshow(data_layer)
#plt.show()

bpff, max_eef2, max_eef3 = bestfocus_library.maxeef(image=data_layer, 
                                                    imagette_size=20,
                                                    verbose=True)



