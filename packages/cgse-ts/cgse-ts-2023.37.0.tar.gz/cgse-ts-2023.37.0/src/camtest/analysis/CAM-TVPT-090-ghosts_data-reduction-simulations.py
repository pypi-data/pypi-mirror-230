#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST PREPARATION

6.9.8 CAM-TVPT-090 Ghosts Characterization

N-CAM

Authors: M. Ammler-von Eiff

Versions:
     2022 01 07  - 0.1 Draft -- script to include reduction of simulated images of opposite CCD (for point-like ghost)
     2022 02 04  - 0.2 Draft -- updated to simulate point-like ghosts for more than a single exposure 


Description:
    Based on CAM-TVPT-090-ghosts_data-reduction.py.
    Opens and reads a background exposure and ghost exposures for V=0 and V=5 each (for a specified source configuration).
    Measures noise levels inside and outside of the camera aperture.
    Stores the result for further offline analysis.

Input parameters (currently edited directly in the code):
    workdir      working directory including measurements or simulated files
    phi          azimuthal angle of source to select ghost exposure(s)
    theta        off-axis angle of source to select ghost exposure(s)
    mag          source brightness to select ghost exposure(s)
    n_exposures  number of ghost exposures   

Output (currently directly edited in the code):
    out_0.fits   stacked ghost image for V=0 source with background subtracted
    out_5.fits   stacked ghost image for V=5 source with background subtracted


Remarks:
    -Make sure that files in the specified configuration do exist in the working directory (currently no automatic check).
    -Make sure to remove old output files (currently no automatic removal of old files)
    -Expected file format is FITS with a filename.
    -The actual analysis is done interactively with the Jupyter notebook in the same folder:
         -definition of masks to measure stellar, ghost, and background levels
         -integration and output of flux in these masks, including error bars

"""

import os

import numpy as np
from astropy.convolution import convolve, Box2DKernel
from astropy.io import fits


def read_fits_data(file):
    hdul = fits.open(file)
    extension_slice = hdul[1]
    header = extension_slice.header
    keyword = "CCD_ID"
    image_read_in_fits = extension_slice.data
    hdul.close()
    return image_read_in_fits


# DATA DIRECTORY
# ==============

# start with test cases
# NOT YET IMPLEMENTED

# check if there is a unique set of calibration images for all configurations
# NOT YET IMPLEMENTED

workdir = os.environ['PLATO_WORKDIR'] + '/ghosts_noise/'


# BACKGROUND
# ==============

# read background images:
bg_data = read_fits_data(workdir + "background.fits")
bg_op_data = read_fits_data(workdir + "opposite_background.fits")

# inspect background image in two locations of 50x50 pixels inside and outside of camera aperture:
sig_bg_inside = np.std(bg_data[3000:3050, 500:550])
sig_bg_outside = np.std(bg_data[500:550, 3000:3050])
print("Background scatter inside of camera aperture [e-]:" + str(sig_bg_inside))
print("Background scatter outside of camera aperture [e-]:" + str(sig_bg_outside))
# image display (not working):
# plt.imshow(bg_data)

# process background images (create smoothed background profile):
bg_smoothed = convolve(bg_data, Box2DKernel(20))
bg_op_smoothed = convolve(bg_op_data, Box2DKernel(20))


# DATA ACCESS
# ==============

# locate, list, and get full-frame FITS files and verify test setup from commanding script:
# number of frames

phi = 45
theta_array = [7]
magnitudes = [10]
n_exposures = 10

for theta in theta_array:
    for magnitude in magnitudes:
        # read a ghost image:
        star_ghost_bg_data = read_fits_data(workdir + "star_ghost_bg_" + str(theta) + "_" + str(phi) + "_" + str(magnitude) + "_0.fits")
        star_ghost_op_bg_data = read_fits_data(workdir + "star_ghost_bg_" + str(theta) + "_" + str(phi) + "_" + str(magnitude) + "_0_opposite.fits")

        # read and stack all other ghost images acquired (if any) to create a deep master image:
        for exposure in range(n_exposures-1):
            print("adding frame " + str(exposure + 1) + " ...")
            theta_phi_mag_str = str(theta) + "_" + str(phi) + "_" + str(magnitude) + "_" + str(exposure + 1)
            star_ghost_bg_data_i = read_fits_data(workdir + "star_ghost_bg_" + theta_phi_mag_str + ".fits")
            star_ghost_bg_data = star_ghost_bg_data + star_ghost_bg_data_i
            star_ghost_op_bg_data_i = read_fits_data(workdir + "star_ghost_bg_" + theta_phi_mag_str + "_opposite.fits")
            star_ghost_op_bg_data = star_ghost_op_bg_data + star_ghost_op_bg_data_i

        # compute average image and subtract background profile:
        star_ghost_data = star_ghost_bg_data / n_exposures - bg_smoothed
        star_ghost_op_data = star_ghost_op_bg_data / n_exposures - bg_op_smoothed

        # save stacked imags for offline inspection:
        hdu_out = fits.PrimaryHDU(star_ghost_data)
        hdu_out_op = fits.PrimaryHDU(star_ghost_op_data)
        hdul_out = fits.HDUList([hdu_out])
        hdul_out_op = fits.HDUList([hdu_out_op])
        hdul_out.writeto(workdir + "out_" + str(magnitude) + ".fits")
        hdul_out_op.writeto(workdir + "out_" + str(magnitude) + "_opposite.fits")
        hdul_out.close()
        hdul_out_op.close()

# display images:
# NOT YET IMPLEMENTED

# measure irradiance ratio if we have an image of the light source:
# NOT YET IMPLEMENTED

# plot relationship between the ghost characteristics and the nominal image:
# (ratio of irradiance, relative position, relative size,...)
# NOT YET IMPLEMENTED
