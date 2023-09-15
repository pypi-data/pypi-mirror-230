#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.7 CAM-TVPT-080 Dynamic range

N-CAM

Authors: C. Paproth

Versions:
    2021 11 03 - 0.1 Draft -- Creation (based on cam_tvpt_010_best_focus_analysis.py written by M. Pertenais)


"""

import astropy.io.fits as pyfits
import sep


def get_centroid_single_image(image):

    """ Calculate centroid of the (single) source in the given image.

    Args:
        - image: Image in which to look for a single (point) sources,
                  represented by a 2D numpy array.

    Returns:
        - row_centroid: Row coordinate of the centroid [pixels].
        - column_centroid: Column coordinate of the centroid [pixels].
    """

    row_centroid = 0
    column_centroid = 0

    weight = 0

    for row in range(image.shape[0]):

        for column in range(image.shape[1]):

            row_centroid += image[row][column] * row
            column_centroid += image[row][column] * column

            weight += image[row][column]

    row_centroid /= weight
    column_centroid /= weight

    return row_centroid, column_centroid



def get_signal(image, mask_size = 3):
    '''
    Parameters
    ----------
    image : np.array 
    mask_size : integer defining the mask size 

    Returns
    -------
    max_sig : signal level of the brightest pixel 
    sum_sig : sum of all pixels in the mask

    '''
    row_centroid, column_centroid = get_centroid_single_image(image)
        
    row_max     = int(min(row_centroid + mask_size / 2, image.shape[0]))
    row_min     = int(max(row_centroid - mask_size / 2, 0))
    column_max  = int(min(column_centroid + mask_size / 2, image.shape[1]))
    column_min  = int(max(column_centroid - mask_size / 2, 0))

    max_sig = 0.0  
    sum_sig = 0.0

    for row in range(row_min, row_max):
        for column in range(column_min, column_max):

            sig = image[row][column]
                
            max_sig = max(max_sig, sig)
            sum_sig = sum_sig + sig
          
    return max_sig, sum_sig


def check_signal(filename, threshold = 40000):
    '''
    Parameters
    ----------
    filename : name of fits file to be checked 
    threshold : threshold for saturation 

    Returns
    -------
    True : if signal is not saturated and if signal is well above noise level 
    False : otherwise

    '''
    
    image = pyfits.open(filename)[2].data

    background = sep.Background(image)
    max_sig, sum_sig = get_signal(image - background.back())


    if max_sig < threshold and sum_sig > 3 * background.globalrms:
        return True
    return False

