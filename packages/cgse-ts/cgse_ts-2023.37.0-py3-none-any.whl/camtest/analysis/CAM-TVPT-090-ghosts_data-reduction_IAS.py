#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.8 CAM-TVPT-090 Ghosts Characterization

N-CAM

Authors: M. Ammler-von Eiff, M Pertenais

Versions:
     2022 09 19  - 1.0 modification of analysis script for IAS data


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
    nonsat       FALSE/TRUE


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

import numpy as np
from astropy.convolution import convolve, Box2DKernel
from astropy.io import fits

from camtest.analysis.functions.fitsfiles import get_image_cube_data, get_image_cube_header

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("fov")
parser.add_argument("nonsat")

args = parser.parse_args()
star_ID = int(args.fov)
nonsat = int(args.nonsat)


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

obsdate='20220801' # date of images taken
obsid= 714  # need to find from data directory specified above [provide integer, will be formatted correctly]

    
# DATA ACQUISITION, PROCESSING, AND STORAGE
# =========================================

# get images for a specified FoV position:

#filenames = cv.fileSelect([f'0{obsid}_','cube','fits'],location=workdir,listOrder=1)
#ffilenames = [workdir+filename for filename in filenames]

#commanding script cam_tvpt_090_ghost.py (version 1.1, 2022-07-15):
theta_array = [1.0, 3.8, 7.0, 8.0, 9.2, 11.4, 13.0, 15.2]
theta_array_nonsat = [1.0, 3.8, 7.0]
phi_array = [45, 135, 225, 315]
num_layer = {"dark":3, "nonsat":19, "sat":6}

#map FoV position to number of dark image:
dark_map = [1,4,7,10,12,14,16,18,20,23,26,29,31,33,35,37,39,42,45,48,50,52,54,56,58,61,64,67,69,71,73,75]

print('Images taken following commanding script v1.1 (nominal):')
i = 0
for phi in phi_array:
    print('FoV position: phi = ',phi)
    for theta in theta_array:
        print('FoV position ',i+1,': theta = ',theta)
        print('FoV position ',i+1,': dark exposure: file ','{:05}'.format(dark_map[i]))
        print('FoV position ',i+1,': saturated exposure: file ','{:05}'.format(dark_map[i]+1))
        if theta in theta_array_nonsat: 
            print('FoV position ',i+1,': non-saturated exposure: file ','{:05}'.format(dark_map[i]+2))
        i=i+1

# GET BACKGROUND PROFILE FOR SUBTRACTION:
print('reading background frames ...')
file_count = dark_map[star_ID-1]
filename = '{:05}'.format(obsid)+'_IAS_N-FEE_CCD_'+'{:05}'.format(file_count)+'_'+obsdate+'_cube.fits'
ffilename = workdir+filename
print('reading {ffilename}')

bg_stacked  = stack_cube_layers(ffilename)

prefix_out = workdir + 'reduced/' + filename
print('writing {prefix_out}')
write_fits_cube(bg_stacked, prefix_out)


print('smoothing background frames ...')
bg_smoothed = bg_stacked
for i in range(0,7):
    bg_smoothed[:,:,i] = convolve(bg_stacked[:,:,i], Box2DKernel(20))

# GET AND STACK saturated GHOST EXPOSURES:
# read and stack images for num_exp ghost exposures

filename = '{:05}'.format(obsid)+'_IAS_N-FEE_CCD_'+'{:05}'.format(dark_map[star_ID-1]+1)+'_'+obsdate+'_cube.fits'
ffilename = workdir+filename
print('reading {ffilename}')
print('stacking image frames ...')
img_stacked = stack_cube_layers(ffilename)
 
# SUBTRACT BACKGROUND:
img_bg = img_stacked - bg_stacked

# Save TO DISK FOR OFFLINE INSPECTION:

prefix_out = workdir + 'reduced/' + filename
print('writing {prefix_out}')
write_fits_cube(img_bg, prefix_out)


# GET AND STACK non-saturated GHOST EXPOSURES:
# read and stack images for num_exp ghost exposures

if nonsat == 1:
    filename = '{:05}'.format(obsid)+'_IAS_N-FEE_CCD_'+'{:05}'.format(dark_map[star_ID-1]+2)+'_'+obsdate+'_cube.fits'
    ffilename = workdir+filename
    print('reading {ffilename}')
    print('stacking image frames ...')
    img_stacked = stack_cube_layers(ffilename)
 
    # SUBTRACT BACKGROUND:
    img_bg = img_stacked - bg_stacked


    # Save TO DISK FOR OFFLINE INSPECTION:

    prefix_out = workdir + 'reduced/' + filename
    print('writing {prefix_out}')
    write_fits_cube(img_bg, prefix_out)

# display images:
# see Jupyter notebook

# measure irradiance ratio if we have an image of the light source:
# will be implemented in Jupyter notebook

# plot relationship between the ghost characteristics and the nominal image:
# (ratio of irradiance, relative position, relative size,...)
# will be implemented in Juptyer notebook
