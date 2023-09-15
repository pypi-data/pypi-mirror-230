#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.8 CAM-TVPT-090 Ghosts Characterization

N-CAM

Authors: M. Ammler-von Eiff, M Pertenais

Versions:
     2021 02 01  - 0.1 Draft -- skeleton script and reading of PlatoSim images
     2021 02 13  - 0.2 Draft -- implemented some analysis commands from ghosts.py
     2021 02 25  - 0.3 Draft -- implemented available analysis commands from ghosts.py
     2021 05 12  - 0.4 Draft -- added noise assessments
     2021 06 03  - 0.5 Draft -- reading and averaging series of extended ghost exposures, subtracting background model,
                                cleaned code, removed checks to verify correct use of simulated image
     2021 08 06  - 0.6 Draft -- established interface with commanding script; intial adaptation to read from test storage location
     2021 08 27  - 0.7 Draft -- adapted to expected fits structure
     2022 04 08  - 0.8 Draft -- adapted to CAM test output at SRON
     2022 04 12  - 0.9 Draft -- enabled selection of a specified FoV and file
     2022 05 17  - 1.0 Draft -- added argument parser to select FoV


Description:
    Reads dark, non-saturated, and saturated exposures for a specified FoV position.
    Includes data reduction steps (stacking, background subtraction) specified in: https://issues.cosmos.esa.int/platowiki/x/ZohNAQ
    Opens and reads background and ghost exposures (data cubes), based on specified site, setup, and obsid.
    Creates a background model.
    Subtracts the background from the ghost exposure.
    Stores images separately for each CCD and each CCD side for further offline analysis.

Input paramaters (currently edited directly in the code):
    workdir      working directory with data (output will be written to subdirectory /reduced)
    obsid        unique test identifier for ghost test (sequential ID, '(I5)')
    star_ID      #FoV position


Output (currently directly edited in the code), for a specified FOV position, and CCD side:
    ogse_ghost_bg_[phi]_[theta]_[fwc_factor]_[ccd_id]_[ccd_side].fits   stacked ghost image with background subtracted


Remarks:
    -Setup is identified via the commanding script configuration in obsid_table.txt.
    -Expected file format is FITS with file suffix '.fits'
    -The actual analysis is done interactively with the Jupyter notebook *.ipynb in the same directory:
         -definition of masks to measure stellar, ghost, and background levels
         -integration and output of flux in these masks, including error bars

"""

import os
from argparse import ArgumentParser

import numpy as np
from astropy.convolution import convolve, Box2DKernel
from astropy.io import fits

from camtest.analysis.functions.fitsfiles import get_image_cube_data, get_image_cube_header

# import convenience as cv

parser = ArgumentParser()
parser.add_argument("fov")

args = parser.parse_args()
star_ID = int(args.fov)


def stack_cube_layers(path):
    ccd_id = ['1','2','3','4']
    # ccd_side: 1 for E and 0 for F
    ccd_side = [1,0]
    image_cube_out = np.zeros((4510,2255,8))
    half_ccd_count = 0
    for id in ccd_id:
        for side in ccd_side:
            image_cube_data = get_image_cube_data(path, id, side)
            image_cube_header = get_image_cube_header(path, id, side)
            #xdim = image_cube_header[0]
            #ydim = image_cube_header[1]
            nexp = image_cube_header[2]
            image_cube_data = image_cube_data[1:nexp-1] # exclude corrupted first layer
            image_cube_avg = np.average(image_cube_data, axis = 0)
            image_cube_out[:,:,half_ccd_count] = image_cube_avg
            half_ccd_count = half_ccd_count + 1
    return image_cube_out

def write_fits_cube(data, prefix):
    ccd_id = ['1','2','3','4']
    ccd_side = ['E','F']
    i = 0
    for id in ccd_id:
        for side in ccd_side:
            file = prefix + '_' + str(id) + str(side) + '.fits'
            try:
                os.remove(file)
            except:
                print('no old FITS file to remove')
            print('writing ', file)
            hdu_out = fits.PrimaryHDU(data[:,:,i])
            hdul_out = fits.HDUList([hdu_out])
            hdul_out.writeto(file)
            hdul_out.close()
            i = i + 1


# DATA DIRECTORY
# ==============

# start with test cases
# NOT YET IMPLEMENTED

# check if there is a unique set of calibration images for all configurations
# NOT YET IMPLEMENTED

# DATA ACCESS
# ==============

# locate and list full-frame FITS files and verify test setup from commanding script:
# number of frames

#workdir = os.environ['PLATO_WORKDIR']
workdir = '/data/'

obsdate='20220224' # date of images taken
obsid= 3054  # need to find from data directory specified above [provide integer, will be formatted correctly]

    
# DATA ACQUISITION, PROCESSING, AND STORAGE
# =========================================

# get images for a specified FoV position:

#filenames = cv.fileSelect([f'0{obsid}_','cube','fits'],location=workdir,listOrder=1)
#ffilenames = [workdir+filename for filename in filenames]

#commanding script cam_tvpt_090_ghost.py (version 0.4 Draft, 2021-11-03):
theta_array = [3.8, 7.6, 11.4, 15.2, 18.88]
phi_array = [0, 30, 60, 90, 135, 225, 315]
num_layer = {"dark":2, "nonsat":11, "sat":3}

print('Images taken following commanding script v0.4 (nominal):')
i = 0
for phi in phi_array:
    print('FoV position: phi = ',phi)
    for theta in theta_array:
        print('FoV position ',i,': theta = ',theta)
        print('FoV position ',i,': dark exposure: file ','{:05}'.format(i*3+1))
        print('FoV position ',i,': non-saturated exposure: file ','{:05}'.format(i*3+2))
        print('FoV position ',i,': saturated exposure: file ','{:05}'.format(i*3+3))
        i = i + 1


# GET BACKGROUND PROFILE FOR SUBTRACTION:
print('reading background frames ...')
file_count = star_ID * 3 + 1
filename = '{:05}'.format(obsid)+'_SRON_N-FEE_CCD_'+'{:05}'.format(file_count)+'_'+obsdate+'_cube.fits'
ffilename = workdir+filename
print('reading {ffilename}')

bg_stacked  = stack_cube_layers(ffilename)

prefix_out = workdir + 'reduced/' + filename
write_fits_cube(bg_stacked, prefix_out)


print('smoothing background frames ...')
bg_smoothed = bg_stacked
for i in range(0,7):
    bg_smoothed[:,:,i] = convolve(bg_stacked[:,:,i], Box2DKernel(20))

# GET AND STACK non-saturated GHOST EXPOSURES:
# read and stack images for num_exp ghost exposures

filename = '{:05}'.format(obsid)+'_SRON_N-FEE_CCD_'+'{:05}'.format(star_ID*3+2)+'_'+obsdate+'_cube.fits'
ffilename = workdir+filename
print('reading {ffilename}')
print('stacking image frames ...')
img_stacked = stack_cube_layers(ffilename)
 
# SUBTRACT BACKGROUND:
img_bg = img_stacked - bg_stacked

# Save TO DISK FOR OFFLINE INSPECTION:

prefix_out = workdir + 'reduced/' + filename
write_fits_cube(img_bg, prefix_out)


# GET AND STACK saturated GHOST EXPOSURES:
# read and stack images for num_exp ghost exposures

filename = '{:05}'.format(obsid)+'_SRON_N-FEE_CCD_'+'{:05}'.format(star_ID*3+3)+'_'+obsdate+'_cube.fits'
ffilename = workdir+filename
print('reading {ffilename}')
print('stacking image frames ...')
img_stacked = stack_cube_layers(ffilename)
 
# SUBTRACT BACKGROUND:
img_bg = img_stacked - bg_stacked


# Save TO DISK FOR OFFLINE INSPECTION:

prefix_out = workdir + 'reduced/' + filename
write_fits_cube(img_bg, prefix_out)

# display images:
# see Jupyter notebook

# measure irradiance ratio if we have an image of the light source:
# will be implemented in Jupyter notebook

# plot relationship between the ghost characteristics and the nominal image:
# (ratio of irradiance, relative position, relative size,...)
# will be implemented in Juptyer notebook
