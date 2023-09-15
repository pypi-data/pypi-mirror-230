#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 12:19:19 2019

@author: pierre
"""

import os
import sep
import numpy as np
import scipy.ndimage as ndi
from astropy.io import fits
from skimage import morphology
import matplotlib.pyplot as plt
import camtest.analysis.convenience as cv
from egse.setup import Setup
from egse.state import GlobalState
from matplotlib import cm

def backgroundSubtraction(image, method="edge", width=10, median_size=None, gauss_sigma=None, verbose=True):
    """
    backgroundSubtraction(image,method="edge",width=10,verbose=True)
    
    image: input image (numpy.array)
    method : in ["edge", "sep"]
        edge : background = median of edge "width" pixels around the image
        sep  : sourceExtractor Background method
    width : see 'method'
    verbose  : boolean, triggers verbose prints
    
    """
    if method.lower().find('edge') >= 0:
        edge = arrayEdge1d(image, width=width)
        result = image.copy() - np.median(edge)
        if verbose:
            print(f"Median Background level (edge): {np.median(edge)}")
        return result, edge

    elif method.lower().find('sep') >= 0 or method.lower().find('sex') >= 0:
        sep_background = sep.Background(image)  # Spatially varying background
        sep_backgroundImage = sep_background.back()  # Evaluate background as 2D array (same dimensions as image)
        result = image - sep_backgroundImage  # Subtract the background
        if verbose:
            print(f"Median Background level (sep): {np.median(sep_backgroundImage)}")
        return result, sep_backgroundImage

    elif method.lower().find("filter") >= 0 or method.lower().find('med') >= 0 or method.lower().find('gau') >= 0:

        if median_size is None:
            median_size = 21
        if gauss_sigma is None:
            gauss_sigma = 11

        # med = ssi.medfilt2d(image, kernel_size=median_size)
        med = ndi.median_filter(image, size=median_size, mode='reflect')
        median_gauss = ndi.gaussian_filter(med, sigma=gauss_sigma, mode='reflect')
        result = image - median_gauss

        if verbose:
            print(f"Median Background level (filter): {np.median(median_gauss)}")

            import matplotlib.pyplot as plt
            plt.figure("backgroundSubtractionBackground")
            plt.imshow(median_gauss, interpolation='nearest', origin='lower')

            plt.figure("backgroundSubtractionResult")
            plt.imshow(result, interpolation='nearest', origin='lower')

        return result, median_gauss

    else:
        print(f"WARNING: method must be in [\"edge\", \"sep\", \"filter\"]")

    return


def arrayEdge1d(array, width=1):
    """
    Returns a 1d array collecting all pixels along the sides of the input array,
    over a number of rows and columns = 'width'
    """
    result = []
    # Add the edges along the rows
    result.extend(np.ravel(array[:width, :]))
    result.extend(np.ravel(array[-width:, :]))
    # Add the edges along the columns (excluding the fraction already included through the rows)
    result.extend(np.ravel(array[width:-width, :width]))
    result.extend(np.ravel(array[width:-width, -width:]))
    return np.array(result)


def setEdges(image, width, value):
    """
    Set "width" rows and columns at the edges of image to value
    """
    image[:width, :] = value
    image[-width:, :] = value
    image[:, :width] = value
    image[:, -width:] = value
    return image


def significantPixels(image, method="yen", width=5, sigma=3, bckgndsub=True, verbose=True):
    import skimage
    import scipy.ndimage as ndi
    import scipy.stats as scis
    if bckgndsub:
        imbckg, back = backgroundSubtraction(image, method='edge', width=width, verbose=verbose)
    else:
        imbckg, back = image, image
    significant = np.zeros_like(image, dtype=bool)
    if method.lower().find("yen") >= 0:
        yen = skimage.filters.threshold_yen(image)
        significant[np.where(image >= yen)] = 1
    elif method.lower().find("global") >= 0 or method.lower().find("sigma") >= 0:
        noise = np.std(back)
        if verbose: print(f"Noise {noise}")
        significant[np.where(imbckg >= sigma * noise)] = 1
    elif method.lower().find("local") >= 0 or method.lower().find("mad") >= 0:
        mad = ndi.generic_filter(image, scis.median_absolute_deviation, size=width)
        significant[np.where(imbckg >= sigma * mad)] = 1
    return significant


def cleanSignificant(significant, method="union"):
    """
    INPUT
    Significant : boolean image marking pixels above the noise
    Method      : in ['cross', 'square', 'union']
                  cross  : cleaning based on binary opening with a structuring element = 3x3 cross
                  square : cleaning based on binary opening with a structuring element = 2x2 square
                  union  : cleaning based on the binary OR of the two solutions above

                  cross is recommended in general
                  union will be necessary for tiny 'islands' of significant pixels (e.g. hartmann spots close to focus).
    OUTPUT
    Map of significant pixels, cleaned from 'islands' smaller than the structuring element(s), i.e.
    typically removing the influence from cosmic rays
    """
    cross = np.zeros([3, 3])
    cross[1, :] = 1
    cross[:, 1] = 1

    square = np.zeros([4, 4])
    square[1:3, 1:3] = 1

    if method.lower().find("cross") >= 0:
        return morphology.binary_opening(significant, selem=cross)
    elif method.lower().find("square") >= 0:
        return morphology.binary_opening(significant, selem=square)
    elif method.lower().find("union") >= 0 or method.lower().find("both") >= 0:
        opencross = morphology.binary_opening(significant, selem=cross)
        opensquare = morphology.binary_opening(significant, selem=square)
        return opencross | opensquare
    else:
        print("Method must be in [cross, square, union]")
        return None


def psfBox(psf, method='sigma', sigma=4, edgeWidth=5, cosmicRemoval=None, kernel=None, verbose=False):
    """
    Locate the psf centroid
    Determine its approximative size
    Extract the corresponding bounding box

    psf : input image

    method in 'canny', 'sigma'
        'canny' --> bounding box of the canny edges
        'sigma' --> bounding box of the pixels 'sigma' sigmas above the background noise

    sigma  :
        method 'canny' : used by the canny edge detection method
        method 'sigma' : used for the thresholding and selection of significant pixels

    edgeWidth : used for the background subtraction
                edgeWidth is the nb of rows and columns at the outer edges of the input image
                that are used for the background estimate

    cosmicRemoval : None or False skipped
                    "open" --> binary opening    (kernel typically = cross)
                    "sum"  --> 2D convolution (kernel typically = square)

    kernel : used in the cosmicRemoval
    """
    from skimage.feature import canny
    # from imageUtils import backgroundSubtraction
    from scipy.ndimage.measurements import center_of_mass as com
    from skimage import morphology
    from scipy.signal import convolve2d
    from skimage.filters.thresholding import threshold_otsu

    # Background subtraction = subtract the average of the "edgeWidth" external rows and columns of the input image
    image, background = backgroundSubtraction(psf, method='edge', width=edgeWidth, verbose=verbose)

    if method.lower().find("canny") >= 0:

        lowThreshold = 0.
        highThreshold = .99
        edges = canny(image, sigma=sigma, low_threshold=lowThreshold, high_threshold=highThreshold, use_quantiles=True)

        xmin, xmax = np.min(np.where(edges)[0]), np.max(np.where(edges)[0])
        ymin, ymax = np.min(np.where(edges)[1]), np.max(np.where(edges)[1])

        xc, yc = com(edges)

    elif method.lower().find("sigma") >= 0:

        noise = np.std(background)
        significant = np.zeros_like(image)
        significant[np.where(image >= sigma * noise)] = 1

    elif method.lower().find("otsu") >= 0:

        othreshold = threshold_otsu(image)
        significant = np.zeros_like(image)
        significant[np.where(image >= sigma * othreshold)] = 1

    else:

        print("WARNING: the method must be in ['canny','sigma']")

    if cosmicRemoval not in [None, False]:

        # COSMIC RAY FILTERING VIA BINARY OPENING (2 filters: min, then max; kernel = cross)
        if cosmicRemoval.lower().find("open") >= 0:

            # Used for cleaning the edges (see below)
            if kernel is None:
                kernelSize = 3
            else:
                kernelSize = np.max(kernel.shape)

            ## Kernel is optional. The cosmic-ray clipping without affecting the shape is actually very good with the default
            ## Default kernel is the smallest possible cross (3x3 square with 0's in the corners)
            ## Default here is None --> skimage.morphology.binary_opening's default
            print("         Filtering First Attempt")
            cleaned = morphology.binary_opening(significant, selem=kernel)

            ## All significant pixels kept within "kernel size" of the edges must be deleted here
            ## Cos if they are the only ones kept, the bounding box doesn't make sense
            setEdges(cleaned, kernelSize, 0)

            # Close to focus the image is very small --> low chance for cosmic
            # BUT the PSF is small, and is cleaned away as a cosmic
            # --> if cleaned image has no single significant pixel left, just ignore the cleaning...
            if len(np.where(cleaned)[0]) > 0:
                significant = cleaned
            else:
                kernel = np.zeros([3, 3])
                kernel[1:, 1:] = 1
                kernel[2, 2] = 0
                cleaned = morphology.binary_opening(significant, selem=kernel)
                setEdges(cleaned, width=3, value=0)
                print("         Filtering Second Attempt")
                if len(np.where(cleaned)[0]) > 0:
                    significant = cleaned
                else:
                    print("         FILTERING SKIPPED")

        # COSMIC RAY FILTERING FOCUSSED ON ISOLATED PIXELS (filter = SUM, kernel = square)
        # Isolated pixels will have a sum of 1
        if cosmicRemoval.lower().find("sum") >= 0:
            print("Sum filtering")
            if kernel is None:
                kernelSize = 10
                kernel = np.ones([kernelSize, kernelSize])
            else:
                kernelSize = np.max(kernel.shape)

            c2d = convolve2d(significant, kernel, mode='same')
            cleaned = significant.copy()
            cleaned[np.where(c2d == 1)] = 0

            # All significant pixels kept within "kernel size" of the edges must be deleted here
            # Cos if they are the only ones kept, the bounding box doesn't make sense
            setEdges(cleaned, kernelSize, 0)
            if len(np.where(cleaned)[0]) > 0:
                significant = cleaned
            else:
                flag = 2
                kernelSizes = [8, 5]
                while flag:
                    print(f"         Filtering attempt: {4 - flag}")
                    kernelSize = kernelSizes[2 - flag]
                    kernel = np.ones([kernelSize, kernelSize])
                    c2d = convolve2d(significant, kernel, mode='same')
                    cleaned = significant.copy()
                    cleaned[np.where(c2d == 1)] = 0
                    if len(np.where(cleaned)[0]) > 0:
                        significant = cleaned
                        flag = 0
                    else:
                        flag -= 1

    # If method == 'canny' --> significant is not defined, and the box is already defined above
    if method.lower().find("canny") < 0:
        xmin, xmax = np.min(np.where(significant)[0]), np.max(np.where(significant)[0])
        ymin, ymax = np.min(np.where(significant)[1]), np.max(np.where(significant)[1])

        xc, yc = com(significant)

    if verbose:
        print(f"Method       : {method}")
        print(f"Filtering    : {cosmicRemoval}")
        print(f"Centroid     : [{xc:8.3f},{yc:8.3f}]")
        print(f"Bounding box : [{xmin},{xmax},{ymin},{ymax}]")

    center = [xc, yc]
    box = [xmin, xmax, ymin, ymax]
    return center, box


def rebin(arr, new_shape):
    """
    Pre-condition : new shape is an exact factor of the old shape

    Example: starting with arr_in or shape (4,6)
             arr_out = rebin(arr_in,new_shape=(2,3))

    From: https://scipython.com/blog/binning-a-2d-array-in-numpy/
    """
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)


def mosaic_fits(filenames, sel_valid, backgnd_sub=True, gauss_filter=20, gap=50, gap_value=25, verbose=True):
    """
    INPUT

    filenames = list of filenames. Expects full paths to _cube*fits
    sel_valid = selection of the valid filenames in the list
                e.g. fileanames = all cubes of an obsid, and cube 0 is empty
                     -> sel_valid = [i for i in range(len(filenames))] -> pop(0)
    gauss_filter : if > 0, interpreted as the kernel size of a gaussian filter and applied to the data.
    gap       : gap between CCDs, in pixels
    gap_value : value set to the pixels in the gap in the final image

    """
    cube_extension = 2

    full, half = 4510, 2255

    ccds_zero_offsets = {'1E': [full + gap, half], '2E': [half, 0], '3E': [0, full + gap],
                         '4E': [full + gap, full + gap],
                         '1F': [full + gap, 0], '2F': [0, 0], '3F': [0, full + gap + half],
                         '4F': [full + gap + half, full + gap]}

    ncubes = len(filenames)

    sumimage = np.zeros([(2 * full) + gap, (2 * full) + gap])
    sumimage[full:full + gap, :] = gap_value
    sumimage[:, full:full + gap] = gap_value

    for cn in range(ncubes):

        if cn not in sel_valid:
            print(f"Skipping cube {cn}")
            continue

        filename = filenames[cn]

        hduc = fits.open(filename)

        ccdid = hduc[2].header["CCD_ID"]
        ccdside = hduc[2].header["SENSOR_SEL"][0]
        rowstart = hduc[0].header["V_START"]
        if hduc[0].header["V_START"] != -hduc[2].header["CRPIX2"]:
            print(f"WARNING {cn=} {hduc[0].header['V_START']=} {-hduc[2].header['CRPIX2']=}")
        # colstart = -hduc[2].header["CRPIX1"]

        sccd = str(ccdid) + ccdside

        cube = np.array(hduc[cube_extension].data, dtype=float)

        if verbose:
            print()
            print(f"Cube {cn:2d} : {filename}   {cube.shape}  CCD {ccdid}{ccdside} {sccd} rowstart {rowstart}")

        if cube.shape[0] == 5:
            print()
            print("WARNING ON CUBE SHAPE {cn} {cube.shape}")
            print()
            cube = cube[1:, :, :]

        cube = np.mean(cube, axis=0)

        if backgnd_sub:
            backgroundMethod = 'filter'
            median_size = [15, 15]
            gauss_sigma = [11, 11]
            cube, background = backgroundSubtraction(np.array(cube, dtype=float), method=backgroundMethod,
                                                     verbose=False, median_size=median_size, gauss_sigma=gauss_sigma)

        if gauss_filter:
            gauss_size = [gauss_filter, gauss_filter]
            cube = ndi.gaussian_filter(cube, sigma=gauss_size, mode='reflect')

        if ccdid == 1:
            cadd = cube[::-1, ::-1]
            size_x, size_y = cadd.shape
            zero_x = ccds_zero_offsets[sccd][0] + full - rowstart - size_x
            zero_y = ccds_zero_offsets[sccd][1]
            sumimage[zero_x:zero_x + size_x, zero_y:zero_y + size_y] += cadd
        elif ccdid == 2:
            cadd = cube.T[::-1, :]
            size_x, size_y = cadd.shape
            zero_x = ccds_zero_offsets[sccd][0]
            zero_y = ccds_zero_offsets[sccd][1] + rowstart
            sumimage[zero_x:zero_x + size_x, zero_y:zero_y + size_y] += cadd
        elif ccdid == 3:
            cadd = cube
            size_x, size_y = cadd.shape
            zero_x = ccds_zero_offsets[sccd][0] + rowstart
            zero_y = ccds_zero_offsets[sccd][1]
            sumimage[zero_x:zero_x + size_x, zero_y:zero_y + size_y] += cadd
        elif ccdid == 4:
            cadd = cube.T[:, ::-1]
            size_x, size_y = cadd.shape
            zero_x = ccds_zero_offsets[sccd][0]
            zero_y = ccds_zero_offsets[sccd][1] + full - rowstart - size_y
            sumimage[zero_x:zero_x + size_x, zero_y:zero_y + size_y] += cadd
        else:
            print(f"WARNING {cn} CCD ID badly defined {ccdid}")

        if verbose:
            print(
                f"     {cn:2d} : {sccd} {ccds_zero_offsets[sccd]} : {rowstart} {size_x} {size_y} --> {zero_x} {zero_y} --> [{zero_x}:{zero_x + size_x}, {zero_y}:{zero_y + size_y}]")

    if verbose:
        cv.imshow(sumimage, figname="sum", figsize=(10, 10), vmin=0, vmax=100,
                  extent=[-full - gap // 2, full + gap // 2, -full - gap // 2, full + gap // 2])

    return sumimage

def get_ccd(cube_number, layer_number, filenames, ccd_number=None, full=False, bckgndsub=False, setup: Setup = None):
    """
    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)
    Returns the 'layer_number'-th layer of that cube

    cube_number = Nth file to pick in the list of filenames
    layer_number = Layer to extract from the cube(s)
    filenames = list of filenames (abs. paths) of the fits datafiles (e.g. belonging to one OBSID)
    ccd_number : optional. If several CCDs are present in the data, allows to select one of them
    full : default = False
           if True, all data are extracted and plotted, including PRE- and OVER-SCAN(S)
           NB: This is modifying the size of the output image, and also the apparent position of the source in the image
               in the column direction, since the columns are organised like this:
                SERIAL-PRESCAN E, IMAGE E, SERIAL OVER-SCAN E, SERIAL_PRESCAN F, IMAGE F, SERIAL_OVERSCAN F

    backgndsub : default = False
                 If True, a smooth background is removed from the each of the image parts
                 The background is estimated from median and gauss filtering.

    setup : egse.setup. Default=None leads to use GlobalState.setup

    Returns the assembled image, of size
        - full = False : 4510 x 4510
        - full = True  : (4510 + n_rows_parallel_overscan), (4510 + sum_of_sizes_of_serial_pre_and_over_scans)
    """
    from astropy.io import fits

    if setup is None:
        setup = GlobalState.setup
    fee_side = setup.camera.fee.ccd_sides.enum
    left_side = fee_side.LEFT_SIDE.name
    right_side = fee_side.RIGHT_SIDE.name

    ccdrows, ccdcols = 4510, 4510

    # OPEN DATA FILE
    filename = filenames[cube_number]
    hduc = fits.open(filename)

    # LIST OF EXTENSIONS
    extnames = ["PRIMARY"]
    extnames.extend(np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object))

    # CHECK WHICH CCD(s) EXIST IN THE DATA
    icubes = np.where([i.find("IMAGE") >= 0 for i in extnames])[0]

    ccds = [hduc[i].header['CCD_ID'] for i in icubes]
    if ccd_number:
        icubes = [i for i in icubes if hduc[i].header['CCD_ID'] == ccd_number]
    elif (len(np.unique(ccds)) == 1):
        ccd_number = np.unique(ccds)[0]
    else:
        print(f"CCDs present in the data: {np.unique(ccds)}")
        print("Make a choice via parameter ccd_number")
        return

    if len(icubes) > 2:
        print("!!!!")
        print(f"WARNING: Nb of half-CCDs expected to be < 2 but = {len(icubes)} > 2")
        print(f"         Check the datastructure")
        print("!!!!")

    indent = ' ' * 8
    # IMAGE EXTRACTION
    img = {'E': None, 'F': None}
    img_nrow = {"E": 0, "F": 0}
    img_ncol = {"E": 0, "F": 0}
    row_start = {"E": 0, "F": 0}
    for ccd_side in ["E", "F"]:
        try:
            iimg = np.where([i.find(f"IMAGE_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
            row_start[ccd_side] = -hduc[iimg].header["CRPIX2"]
            print(f"IMAGE_{ccd_number}_{ccd_side} -- ext {iimg}: {extnames[iimg]}")

            if bckgndsub:

                median_size = [15, 15]
                gauss_sigma = [11, 11]
                cube, background = backgroundSubtraction(np.array(hduc[iimg].data[layer_number, :, :], dtype=float),
                                                         method='filter', verbose=False,
                                                         median_size=median_size, gauss_sigma=gauss_sigma)
                img[ccd_side] = cube

            else:

                img[ccd_side] = np.array(hduc[iimg].data[layer_number, :, :], dtype=float)

            img_nrow[ccd_side], img_ncol[ccd_side] = img[ccd_side].shape
        except:
            print(f"{indent}No {ccd_side}-side Image Found")

    if full:

        # EXTRACTION OF PRE & OVERSCANS
        spre = {"E": None, "F": None}
        sover = {"E": None, "F": None}
        pover = {"E": None, "F": None}

        spre_nrow = {"E": 0, "F": 0}
        spre_ncol = {"E": 0, "F": 0}
        sover_nrow = {"E": 0, "F": 0}
        sover_ncol = {"E": 0, "F": 0}
        pover_nrow = {"E": 0, "F": 0}
        pover_ncol = {"E": 0, "F": 0}

        for ccd_side in ["E", "F"]:
            try:
                ispre = np.where([i.find(f"SPRE_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                spre[ccd_side] = np.array(hduc[ispre].data[layer_number, :, :], dtype=float)
                spre_nrow[ccd_side], spre_ncol[ccd_side] = spre[ccd_side].shape
                print(f"SPRE_{ccd_number}_{ccd_side} -- ext {ispre}: {extnames[ispre]}")
            except:
                print(f"{indent}No {ccd_side}-side Serial Prescan Found")
            try:
                isover = np.where([i.find(f"SOVER_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                sover[ccd_side] = np.array(hduc[isover].data[layer_number, :, :], dtype=float)
                sover_nrow[ccd_side], sover_ncol[ccd_side] = sover[ccd_side].shape
                print(f"SOVER_{ccd_number}_{ccd_side} -- ext {isover}: {extnames[isover]}")
            except:
                print(f"{indent}No {ccd_side}-side Serial Overscan Found")
            try:
                ipover = np.where([i.find(f"POVER_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0]
                pover[ccd_side] = np.array(hduc[ipover].data[layer_number, :, :], dtype=float)
                pover_nrow[ccd_side], pover_ncol[ccd_side] = pover[ccd_side].shape
                print(f"POVER_{ccd_number}_{ccd_side} -- ext {ipover}: {extnames[ipover]}")
            except:
                print(f"{indent}No {ccd_side}-side Parallel Overscan Found")

        if (spre["E"] is not None) and (spre["F"] is not None) and (spre_ncol["E"] != spre_ncol["F"]):
            print(
                f"CRITICAL : serial prescans show diff. sizes for E and F. nb cols E:{spre_ncol['E']}, F:{spre_ncol['F']}")
        if (sover["E"] is not None) and (sover["F"] is not None) and (sover_ncol["E"] != sover_ncol["F"]):
            print(
                f"CRITICAL : serial overscans show diff. sizes for E and F. nb cols E:{sover_ncol['E']}, F:{sover_ncol['F']}")
        if (pover["E"] is not None) and (pover["F"] is not None) and (pover_ncol["E"] != pover_ncol["F"]):
            print(
                f"CRITICAL : parallel overscans show diff. sizes for E and F. nb rows E:{pover_nrow['E']}, F:{pover_nrow['F']}")

        # Glue everything together

        spre_colstart = {left_side: 0,
                         right_side: ccdcols + spre_ncol[left_side] + sover_ncol[left_side] + sover_ncol[right_side]}
        spre_colend = {left_side: spre_ncol[left_side],
                       right_side: spre_colstart[right_side] + spre_ncol[right_side]}
        sover_colstart = {left_side: spre_ncol[left_side] + 2255,
                          right_side: spre_ncol[left_side] + 2255 + sover_ncol[left_side]}
        sover_colend = {left_side: sover_colstart[left_side] + sover_ncol[left_side],
                        right_side: sover_colstart[right_side] + sover_ncol[right_side]}
        pover_colstart = {left_side: spre_ncol[left_side],
                          right_side: sover_colend[right_side]}
        img_colstart = {left_side: spre_ncol[left_side],
                        right_side: sover_colend[right_side]}

        # ASSEMBLY OF FULL-IMAGE FROM VARIOUS COMPONENTS
        fullimage = np.zeros([ccdrows + pover_nrow["E"],
                              ccdcols + spre_ncol["E"] + spre_ncol[right_side] + sover_ncol["E"] + sover_ncol["F"]])

        for ccd_side in ["E", "F"]:
            # IMAGE
            fullimage[row_start[ccd_side]: row_start[ccd_side] + img_nrow[ccd_side],
            img_colstart[ccd_side]:img_colstart[ccd_side] + img_ncol[ccd_side]] = img[ccd_side]

            # PRE & OVERSCANS
            if (spre[ccd_side] is not None):
                fullimage[row_start[ccd_side]:row_start[ccd_side] + spre_nrow[ccd_side],
                spre_colstart[ccd_side]:spre_colend[ccd_side]] = spre[ccd_side]
            if (sover[ccd_side] is not None):
                fullimage[row_start[ccd_side]:row_start[ccd_side] + sover_nrow[ccd_side],
                sover_colstart[ccd_side]:sover_colend[ccd_side]] = sover[ccd_side]
            if (pover[ccd_side] is not None):
                fullimage[ccdrows:ccdrows + pover_nrow[ccd_side],
                pover_colstart[ccd_side]:pover_colstart[ccd_side] + pover_ncol[ccd_side]] = pover[ccd_side]
    else:

        # Glue everything together

        img_colstart = {left_side: 0, right_side: 2255}

        fullimage = np.zeros([ccdrows, ccdcols], dtype=float)
        for ccd_side in ["E", "F"]:
            fullimage[row_start[ccd_side]:row_start[ccd_side] + img_nrow[ccd_side],
            img_colstart[ccd_side]:img_colstart[ccd_side] + img_ncol[ccd_side]] = img[ccd_side]

    return fullimage


def show_ccd(cube_number, layer_number, filenames, ccd_number=None, vsigma=2, obsid=None, full=False, bckgndsub=False,
             **kwargs):
    """
    show_ccd(cube_number, layer_number, filenames, ccd_number=None, vsigma=2, obsid=None, full=False, bckgndsub=False, **kwargs)
    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)
    Displays the 'layer_number'-th layer of that cube

    cube_number = Nth file to pick in the list of filenames
    layer_number = Layer to extract from the cube(s)
    filenames = list of filenames (abs. paths) of the fits datafiles (e.g. belonging to one OBSID)
    ccd_number : optional. If several CCDs are present in the data, allows to select one of them
    vsigma : display parameter (automatic z-scale)
    obsid  = for plot decoration
    full : default = False
           if True, all data are extracted and plotted, including PRE- and OVER-SCAN(S)
           NB: This is modifying the size of the output image, and also the apparent position of the source in the image
               in the column direction, since the columns are organised like this:
                SERIAL-PRESCAN E, IMAGE E, SERIAL OVER-SCAN E, SERIAL_OVER-SCAN F, IMAGE F, SERIAL PRE-SCAN F
    backgndsub : default = False
                 If True, a smooth background is removed from the each of the image parts
                 The background is estimated from median and gauss filtering.
    **kwargs : for plot decoration


    Returns the assembled image, of size
        - full = False : 4510 x 4510
        - full = True  : (4510 + n_rows_parallel_overscan), (4510 + sum_of_sizes_of_serial_pre_and_over_scans)

    """
    from matplotlib import cm

    kwargs.setdefault('cmap', cm.inferno)

    # Get the Image
    fullimage = get_ccd(cube_number=cube_number, layer_number=layer_number, filenames=filenames, ccd_number=ccd_number,
                        full=full, bckgndsub=bckgndsub)

    # PLOT
    cv.imshow(fullimage, vsigma=vsigma, **kwargs)

    plt.colorbar()

    if ccd_number is None:
        # One single CCD in the data, let's rederive the number
        filename = filenames[cube_number]
        hduc = fits.open(filename)
        extnames = ["PRIMARY"]
        extnames.extend(np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object))
        iimg = np.where([i.find(f"IMAGE") >= 0 for i in extnames])[0][0]
        ccd_number = extnames[iimg].split("_")[1]

    plt.title(f"{obsid=} cube={cube_number} layer={layer_number} CCD {ccd_number}", size=20)

    return fullimage


def get_allccds(cube_number, layer_number, filenames, full=False, bckgndsub=False):
    """
    show_allccds(cube_number, layer_number, filenames, vsigma=2, obsid=None, full=False, bckgndsub=False, **kwargs)
    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)
    Displays the 'layer_number'-th layer of that cube

    cube_number = Nth file to pick in the list of filenames
    layer_number = Layer to extract from the cube(s)
    filenames = list of filenames (abs. paths) of the fits datafiles (e.g. belonging to one OBSID)
    full : default = False
           if True, all data are extracted and plotted, including PRE- and OVER-SCAN(S)
           NB: This is modifying the size of the output image, and also the apparent position of the source in the image
               in the column direction, since the columns are organised like this:
                SERIAL-PRESCAN E, IMAGE E, SERIAL OVER-SCAN E, SERIAL_OVER-SCAN F, IMAGE F, SERIAL PRE-SCAN F
    backgndsub : default = False
                 If True, a smooth background is removed from the each of the image parts
                 The background is estimated from median and gauss filtering.

    Returns the assembled image, of size
        - full = False : 4510 x 4510
        - full = True  : (4510 + n_rows_parallel_overscan), (4510 + sum_of_sizes_of_serial_pre_and_over_scans)

    """
    # GET THE IMAGES
    images = {1: None, 2: None, 3: None, 4: None}
    shapes = None
    for ccd_number in [1, 2, 3, 4]:
        # try:
        img = get_ccd(cube_number=cube_number, layer_number=layer_number, filenames=filenames, ccd_number=ccd_number,
                      full=full, bckgndsub=bckgndsub)
        images[ccd_number] = img
        # Verify that all images have the same size
        if shapes is None:
            shapes = img.shape
        else:
            if img.shape != shapes:
                print("CRITICAL: NOT ALL IMAGES HAVE THE SAME SHAPE. Please check the data")
                print(f"{ccd_number=}, {img.shape=} vs shape found for another CCD: {shapes}")
        # except:
        #     print(f"No image was found for CCD {ccd_number}")

    # CONSTRUCT THE FOCAL-PLANE IMAGE
    # We assume the images of all CCDs have the same size (checked above)

    # Position of "lower-left" pixel (looking at the focal plane with CCD1 on top-left)
    if shapes is None:
        print("CRITICAL: NO IMAGE FOUND")
        return
    else:
        nrows, ncols = shapes

    if nrows >= ncols:
        long_side, short_side = 0, 1
    else:
        long_side, short_side = 1, 0

    ccds_zero_offsets = {}
    ccds_zero_offsets[4] = [shapes[long_side], shapes[long_side]]
    ccds_zero_offsets[3] = [shapes[long_side], shapes[long_side] - nrows]
    ccds_zero_offsets[2] = [shapes[long_side] - nrows, shapes[long_side] - ncols]
    ccds_zero_offsets[1] = [shapes[long_side] - ncols, shapes[long_side]]

    fullimage = np.zeros([shapes[long_side] * 2, shapes[long_side] * 2], dtype=float)

    if images[1] is not None:
        print(f"1:  [{ccds_zero_offsets[1][1]}:{ccds_zero_offsets[1][1] + nrows}, \
        {ccds_zero_offsets[1][0]}:{ccds_zero_offsets[1][0] + ncols}]")
        fullimage[ccds_zero_offsets[1][1]:ccds_zero_offsets[1][1] + nrows,
        ccds_zero_offsets[1][0]:ccds_zero_offsets[1][0] + ncols] = images[1][::-1, ::-1]
    if images[2] is not None:
        print(f"2:  [{ccds_zero_offsets[2][1]}:{ccds_zero_offsets[2][1] + ncols},\
            {ccds_zero_offsets[2][0]}:{ccds_zero_offsets[2][0] + nrows}]")
        fullimage[ccds_zero_offsets[2][1]:ccds_zero_offsets[2][1] + ncols,
        ccds_zero_offsets[2][0]:ccds_zero_offsets[2][0] + nrows] = images[2].T[::-1, :]
    if images[3] is not None:
        print(f"3:  [{ccds_zero_offsets[3][1]}:{ccds_zero_offsets[3][1] + nrows},\
        {ccds_zero_offsets[3][0]}:{ccds_zero_offsets[3][0] + ncols}]")
        fullimage[ccds_zero_offsets[3][1]:ccds_zero_offsets[3][1] + nrows,
        ccds_zero_offsets[3][0]:ccds_zero_offsets[3][0] + ncols] = images[3]
    if images[4] is not None:
        print(f"4:  [{ccds_zero_offsets[4][1]}:{ccds_zero_offsets[4][1] + ncols},\
        {ccds_zero_offsets[4][0]}:{ccds_zero_offsets[4][0] + nrows}]")
        fullimage[ccds_zero_offsets[4][1]:ccds_zero_offsets[4][1] + ncols,
        ccds_zero_offsets[4][0]:ccds_zero_offsets[4][0] + nrows] = images[4].T[:, ::-1]

    return fullimage


def show_allccds(cube_number, layer_number, filenames, vsigma=2, obsid=None, full=False, bckgndsub=False, **kwargs):
    """
    show_allccds(cube_number, layer_number, filenames, vsigma=2, obsid=None, full=False, bckgndsub=False, **kwargs)
    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)
    Displays the 'layer_number'-th layer of that cube

    cube_number = Nth file to pick in the list of filenames
    layer_number = Layer to extract from the cube(s)
    filenames = list of filenames (abs. paths) of the fits datafiles (e.g. belonging to one OBSID)
    vsigma : display parameter (automatic z-scale). Using vmin & vmax (as kwargs) will overrule this.
    obsid  = for plot decoration
    full : default = False
           if True, all data are extracted and plotted, including PRE- and OVER-SCAN(S)
           NB: This is modifying the size of the output image, and also the apparent position of the source in the image
               in the column direction, since the columns are organised like this:
                SERIAL-PRESCAN E, IMAGE E, SERIAL OVER-SCAN E, SERIAL_OVER-SCAN F, IMAGE F, SERIAL PRE-SCAN F
    backgndsub : default = False
                 If True, a smooth background is removed from the each of the image parts
                 The background is estimated from median and gauss filtering.
    **kwargs : for plot decoration


    Returns the assembled image, of size
        - full = False : 4510 x 4510
        - full = True  : (4510 + n_rows_parallel_overscan), (4510 + sum_of_sizes_of_serial_pre_and_over_scans)

    """
    from matplotlib import cm

    kwargs.setdefault('cmap', cm.inferno)

    fullimage = get_allccds(cube_number=cube_number, layer_number=layer_number, filenames=filenames, full=full,
                            bckgndsub=bckgndsub)

    # PLOT
    cv.imshow(fullimage, vsigma=vsigma, **kwargs)

    plt.colorbar()
    plt.title(f"{obsid=} cube={cube_number} layer={layer_number}", size=20)

    return fullimage


def get_extnames(cube_number, filenames, verbose=True):
    """
    Extracts the extension names from file "cube_number" in the input list of fits filenames
    """
    from astropy.io import fits

    # OPEN DATA FILE
    filename = filenames[cube_number]
    hduc = fits.open(filename)

    # LIST OF EXTENSIONS
    extnames = ["PRIMARY"]
    extnames.extend(np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object))

    if verbose:
        hduc.info()
        print()

    return extnames


def get_extension(cube_number, filenames, extension):
    """
    Extracts the data from a given extension in a list of fits filenames (e.g. 1 obsid)
    """
    from astropy.io import fits

    # OPEN DATA FILE
    filename = filenames[cube_number]
    hduc = fits.open(filename)

    return hduc[extension]


def get_layer(cube_number, layer_number, filenames, extension, rowrange=None, colrange=None):
    """
    get_layer(cube_number, layer_number, filenames, extension, rowrange=None, colrange=None)

    Extracts the data from a layer of given extension in a list of fits filenames (e.g. 1 obsid)

    cube_number : item (cube) to extract from the list of (fits) filenames
    layer_number : layer number
    filenames : list of fits files containing the data, e.g. for one obsid
    extension : extension (number or name) to extract from the fits file. Default = 2 = first IMAGE extension
    rowrange : [rowmin, rowmax] allows to select part of the image
    colrange : [colmin, colmax] allows to select part of the image
    """
    ext = get_extension(cube_number=cube_number, filenames=filenames, extension=extension)

    layer = ext.data[layer_number, :, :]
    if rowrange:
        layer = layer[rowrange[0]:rowrange[1], :]
    if colrange:
        layer = layer[:, colrange[0]:colrange[1]]

    return layer


def show_single(obsid, cube_number, layer_number, extension_number=2, datadir=None, vsigma=2):
    """
    obsid       : int: observation id
    cube_number : int: "FoV position number" (counting from 0)
    layer_number: int: image acquisition number (at given FoV position, counting from 0)
    extension_number=2: int: fits extension number. If in doubt, open the fits file hdu=fits.open(file) then hdu.info()
    datadir=None : directory where the data are stored. Default = env. variable "PLATO_LOCAL_DATA_LOCATION"
    vsigma=2   : float : controls the contrast in the image (the lower vsigma, the higher the contrast)
    """
    if datadir is None:
        datadir = os.getenv("PLATO_LOCAL_DATA_LOCATION")

    sobsid = str(obsid).zfill(5)

    obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
    filenames = cv.fileSelect([f'{sobsid}_', 'cube', 'fits'], location=datadir + obsidir)
    ffilenames = [datadir + obsidir + filename for filename in filenames]

    cv.print1(ffilenames)
    print(f"{len(ffilenames)} fits files were found for obsid {obsid}")

    print(f"The selected fits file is {ffilenames[cube_number]}")
    print(f"It is structured as follows:")
    hduc = fits.open(ffilenames[cube_number])
    hduc.info()

    thisplot = show_layer(cube_number=cube_number, layer_number=layer_number, filenames=ffilenames, extension=extension_number, obsid=obsid, rowrange=None, colrange=None, vsigma=vsigma, cmap=cm.inferno)

    return thisplot


def show_layer(cube_number, layer_number, filenames, extension=2, obsid=None, rowrange=None, colrange=None, vsigma=2,
               **kwargs):
    """
    Extracts the data from a layer of given extension in a list of fits filenames (e.g. 1 obsid) and displays it

    Inputs: most parameters are described in get_layer.__doc__
    obsid  : only used for plot decoration
    vsigma : helps to automatically fix the z-range. Using vmin & vmax (as kwargs) will overrule this)
    """
    from matplotlib import cm
    kwargs.setdefault('cmap', cm.inferno)

    layer = get_layer(cube_number=cube_number, layer_number=layer_number, filenames=filenames, extension=extension,
                      rowrange=rowrange, colrange=colrange)

    # PLOT
    cv.imshow(layer, vsigma=vsigma, **kwargs)

    plt.colorbar()
    plt.title(f"{obsid=} cube={cube_number} {extension=} layer={layer_number}", size=20)

    return plt.gcf()


def show_extension(cube_number, layer_number, filenames, extension, vsigma=2, obsid="", **kwargs):
    """
    showExt(cube_number, layer_number, filenames, extension, vsigma=2, title=None, **kwargs)
    """
    from matplotlib import cm

    kwargs.setdefault('cmap', cm.inferno)

    ext = get_extension(cube_number=cube_number, filenames=filenames, extension=extension)

    cv.imshow(ext.data[layer_number, :, :], vsigma=vsigma, **kwargs)

    plt.title(f"OBSID {obsid}\nCube {cube_number}   {ext.header['EXTNAME']}   Layer {layer_number}")

    return ext


def show_profile(cube_number, layer_number, filenames, extension, rowcol='row', rowrange=None, colrange=None, avg=1,
                 offset=0., rainbow=False, legend=False, figname=None, labelavg=None, **kwargs):
    """
    show_profile(cube_number, layer_number, filenames, extension, rowcol='row', rowrange=None, colrange=None, avg=1, offset=0., rainbow=False,legend=False, figname=None, **kwargs)

    Parameters
    ----------

    cube_number : int. selected fits file in 'filenames'
    filenames   : list of fits filenames (e.g. belonging to an obsid); full paths
    extension   : extension to be extracted from the fits file
                  The extension can be an int or a string
    rowcol in ['row', 'col'] : specifies the desired type of profile,
                  e.g. 'row' will display rows and compute the average row
    rowrange, colrange : [min, max] allows to select part of the input data
                  These refer to the shape of the dataset, not to their location on the CCD, which may differ esp.
                  in the case of partial readout.
    avg : display the average profile along the given direction
          avg = 1 : display rows|cols and their average profile
          avg = 0 : don't display the average profile
          avg = 2 : display only the average profile
    labelavg : label for the avg curve in the plot legend
    offset: display option : offset to apply between every row or column
    rainbow : False : gray colors; True : full colors
    legend  : False by default. True : include the row|col number in the legend
    kwargs : plt.plot kwargs (only applied to the average profile)

    """
    data = get_layer(cube_number=cube_number, layer_number=layer_number, filenames=filenames, extension=extension,
                     rowrange=rowrange, colrange=colrange)

    print(f"{data.shape=}")

    haxis = {'row': 0, 'col': 1}
    hnb = {'row': data.shape[0], 'col': data.shape[1]}

    if figname:
        plt.figure(figname)

    x = None
    if avg < 2:
        if avg == 0:
            darkest = 0.
        else:
            darkest = 0.3
        if rainbow:
            colors = cv.colors_gen(n=hnb[rowcol])
        else:
            colors = cv.grays_gen(n=hnb[rowcol], darkest=darkest)

        label = None
        if rowcol.find('row') >= 0:
            x = np.arange(data.shape[1])
            if colrange is not None:
                x = x + colrange[0]
            for irow in range(hnb[rowcol]):
                if legend: label = f"row {irow}"
                plt.plot(x, data[irow, :] + offset * irow, c=colors[irow], label=label)#, **kwargs)
            plt.xlabel("Data Column")
        elif rowcol.find('col') >= 0:
            x = np.arange(data.shape[0])
            if rowrange is not None:
                x = x + rowrange[0]
            for icol in range(hnb[rowcol]):
                if legend: label = f"col {icol}"
                plt.plot(x, data[:, icol] + offset * icol, c=colors[icol], label=label)#, **kwargs)
            plt.xlabel('Data Row')

    if avg > 0:

        mprofile = np.mean(data, axis=haxis[rowcol])

        x = np.arange(mprofile.shape[0])
        if (rowcol.find('col') >= 0) and (rowrange is not None):
            x += rowrange[0]
        elif (rowcol.find('row') >= 0) and (colrange is not None):
            x += colrange[0]

        if labelavg is None:
            labelavg = f"Avg {rowcol} profile"

        kwargs.setdefault("c", "k")
        plt.plot(x, mprofile, lw=3, label=labelavg, **kwargs)
        plt.legend()

    if rowcol.find('row') >= 0:
        plt.xlabel("Data Column")
    elif rowcol.find('col') >= 0:
        plt.xlabel('Data Row')
    plt.grid(alpha=0.25)


def obsid_overview_htm(obsid, filenames, layer_number, outputdir, bckgndsub=False, htm_columns=2, verbose=True):
    """
    obsid : obsid [used for plot decoration]
    filenames : full paths to the fits files to be used for the overview
    layer_number : layer to be extracted from every image cube
    outputdir : where the images are saved
    full : if True, all pre- and over-scans are included in the image (default=False)
    bckgndsub : if True a background subtraction in included (based on median and gauss filtering).
                Note that this is time-consuming. Default=False

    htm_columns : nb of columns in the output HTML table of images (default = 2)

    OUTPUT:
    overview_<obsid> directory, containing
        . 1 image / cube in the obsid
        . 1 htm file

    In Confluence:
    . Create a new page, give it a title and hit "Publish"
    . In that new page, hit "Edit"
    . Click "Open in source editor" (<> icon top right of the page)
    . BEFORE NEXT STEP: Upload all the images generated by this script
    . copy all files indicated so in the html file written by this script and paste them in the source of the Confluence page
    """
    overviewdir = outputdir + f"/overview_obsid_{obsid}/"
    if not os.path.exists(overviewdir):
        os.mkdir(overviewdir)

    # Create the images
    plotnames = obsid_overview_images(obsid, filenames, layer_number, overviewdir, bckgndsub=bckgndsub)

    nplots = len(plotnames)
    htm_rows = nplots // htm_columns

    f = open(overviewdir + f"overview_obsid_{obsid}.htm", 'w')
    f.write("<HTML>\n")
    f.write("<HEAD>\n")
    f.write(f'<title> Overview obsid {obsid} </title>\n')
    f.write("</HEAD>\n")
    f.write("<BODY>\n")

    f.write("\n\n<!-- COPY PASTE FROM HERE TO WHERE INDICATED IN/AS THE SOURCE CODE OF YOUR NEW CONFLUENCE PAGE -->\n")

    f.write(f'<p class="auto-cursor-target"> Overview obsid {obsid} </p>\n<BR/>\n')

    f.write('<table class="wrapped">\n')
    f.write('<colgroup> <col style="width: 525.0px;"/> <col style="width: 29.0px;"/> </colgroup>\n')
    f.write('<tbody>\n')

    c = -1
    for table_row in range(htm_rows):
        f.write("<tr>\n")
        for table_col in range(htm_columns):
            c += 1
            f.write('<td>\n')
            f.write('<div class="content-wrapper">\n')
            f.write('<p><br/></p>\n')
            f.write('</div>\n')
            try:
                plotname = plotnames[c].split('/')[-1]
                f.write('<ac:image ac:height="250">\n')
                f.write(f' <ri:attachment ri:filename="{plotname}"/>\n')
                f.write('</ac:image>\n')
            except:
                print(f"{c=} couldn't find plotnames[c]")
                pass
            f.write('</td>\n')
        f.write("</tr>\n")
    f.write("</tbody>\n")
    f.write("</table>\n")
    f.write('<p class="auto-cursor-target"> <br/> </p>\n')

    f.write("<!-- END OF THE TEXT TO COPY TO YOUR CONFLUENCE PAGE -->\n\n")

    f.write("</BODY>\n")
    f.write("</HTML>\n")
    f.close()
    return


def obsid_overview_images(obsid, filenames, layer_number, outputdir, full=False, bckgndsub=False):
    """
    obsid : obsid [used for plot decoration]
    filenames : full paths to the fits files to be used for the overview
    layer_number : layer to be extracted from every image cube
    outputdir : where the images are saved
    full : if True, all pre- and over-scans are included in the image (default=False)
    bckgndsub : if True a background subtraction in included (based on median and gauss filtering).
                Note that this is time-consuming. Default=False

    Returns the list of filenames of the plots = the absolute paths to the plots
    """
    plotnames = []

    if isinstance(obsid, int):
        sobsid = str(obsid).zfill(5)
    else:
        sobsid = obsid

    for cn in range(len(filenames)):
        plt.close()
        fimg = show_allccds(cn, layer_number, filenames, vsigma=2, obsid=obsid, full=full, bckgndsub=bckgndsub)
        plotname = outputdir + f"obsid_{sobsid}_cube_{str(cn).zfill(2)}_layer_{layer_number}_allccds.png"
        plt.savefig(plotname)
        plotnames.append(plotname)
        print(f"Image creation - Cube {cn}  -->  {plotname}")
        print()

    return plotnames


def get_pixels_in_time(cube_number, filenames, ccd_number=None, ccd_side="E", setup=None, serial=False, parallel=False):
    """

    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)

    Extract the pixel values, by chronological order of acquisition

    cube_number = Nth file to pick in the list of filenames
    filenames = list of filenames (abs. paths) of the fits datafiles (e.g. belonging to one OBSID)
    ccd_number : optional. If several CCDs are present in the data, allows to select one of them
    ccd_side   : 'E' or 'F'
    serial     : bool : include serial pre- and over-scans or not
    parallel   : bool : include parallel overscan or not
    full : default = False
           if True, all data are extracted and plotted, including PRE- and OVER-SCAN(S)
           NB: This is modifying the size of the output image, and also the apparent position of the source in the image
               in the column direction, since the columns are organised like this:
                SERIAL-PRESCAN E, IMAGE E, SERIAL OVER-SCAN E, SERIAL_OVER-SCAN F, IMAGE F, SERIAL PRE-SCAN F
    """
    from camtest import GlobalState

    if setup is None:
        setup = GlobalState.setup

    n_serial_prescan = setup.camera.fee.n_serial_prescan
    n_serial_overscan = setup.camera.fee.n_serial_overscan
    time_row_parallel = setup.camera.fee.time_row_parallel
    time_pixel_readout = setup.camera.fee.time_pixel_readout

    # OPEN DATA FILE
    filename = filenames[cube_number]
    hduc = fits.open(filename)

    # LIST OF EXTENSIONS
    extnames = ["PRIMARY"]
    extnames.extend(np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object))

    # FRAME TIMES
    frame_times = cv.get_frame_times([filenames[cube_number]], ccd_number, ccd_side)

    # CHECK WHICH CCD(s) EXIST IN THE DATA
    icubes = np.where([i.find("IMAGE") >= 0 for i in extnames])[0]

    ccds = [hduc[i].header['CCD_ID'] for i in icubes]
    if ccd_number:
        icubes = [i for i in icubes if hduc[i].header['CCD_ID'] == ccd_number]
    elif (len(np.unique(ccds)) == 1):
        ccd_number = np.unique(ccds)[0]
    else:
        print(f"CCDs present in the data: {np.unique(ccds)}")
        print("Make a choice via parameter ccd_number")
        return None

    if len(icubes) > 2:
        print("!!!!")
        print(f"WARNING: Nb of half-CCDs expected to be < 2 but = {len(icubes)} > 2")
        print(f"         Check the datastructure")
        print("!!!!")

    if ccd_side not in ["E", "F"]:
        print(f"CRITICAL: {ccd_side=} It must be either E or F. Aborting")
        return None

    if serial:
        raise NotImplementedError
    else:
        data_cube = hduc[f"IMAGE_{ccd_number}_{ccd_side}"].data
        time_cube = np.zeros_like(data_cube, dtype=float)
        nlayers, nrows, ncols  = data_cube.shape

        time_row_full = time_row_parallel + ((ncols + n_serial_prescan + n_serial_overscan) * time_pixel_readout)

        relative_time_row = np.array([(time_pixel_readout*col) for col in range(ncols)])

        relative_time_image = np.zeros([nrows, ncols], dtype=float)
        for row in range(nrows):
            relative_time_image[row,:] = relative_time_row + (row * time_row_full)

        for ln in range(nlayers):
            time_cube[ln, :, :] = relative_time_image + frame_times[ln]

        result_data = np.reshape(data_cube, [nlayers, nrows*ncols])
        result_times = np.reshape(time_cube, [nlayers, nrows*ncols])

        if parallel:
            raise NotImplementedError

    return result_times, result_data


