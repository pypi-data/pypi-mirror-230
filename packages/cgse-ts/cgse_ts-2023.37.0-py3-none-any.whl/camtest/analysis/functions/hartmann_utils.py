from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from astropy.io import fits
from astropy.table import Table
from camtest import load_setup
import camtest.analysis.convenience as cv
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates, angles_to_focal_plane_coordinates

def get_tau(elevation, setup=None):
    """
    Interpolates the value of 'tau' in setup.camera.fov.tau
    """
    from camtest import GlobalState
    from scipy.interpolate import interp1d

    print(f"{setup=}")
    if setup is None:
        setup = GlobalState.setup

    cal_theta = np.array(setup.camera.fov.tau[0])
    cal_tau = np.array(setup.camera.fov.tau[1])
    # cal_theta = np.array([3.1, 8.3, 12.4, 16.33])
    # cal_tau = np.array([65, 65, 60, 50])

    f = interp1d(cal_theta, cal_tau, kind='linear', fill_value="extrapolate")

    return f(elevation)

def cosine_funcfixf(x, amplitude, phase, offset):
    return np.cos(x * 2. * np.pi / 360. + phase) * amplitude + offset


def get_hartmann_ellipse(cube,median_size=[1,15,15],gauss_sigma=[0,11,11],centroiding=True,cleaning=True,backgnd_sub=True,threshold='yen',mad_sigma=3,mad_width=15,verbose=True, skip_layer_0=True, layer_selection=None, clean_pattern=True, neighbour=1):
    """
    get_hartmann_ellipse(cube,median_size=[1,15,15],gauss_sigma=[0,11,11],centroiding=True,cleaning=True,backgnd_sub=True,threshold='yen',mad_sigma=3,mad_width=15,verbose=True, skip_layer_0=True, layer_selection=None, clean_pattern=True, neighbour=1)

    INPUT
    cube : data cube or single image

    median_size, gauss_sigma : used by the backgroundSubtraction routine. See that function in image_utils

    centroiding : bool. pass only the centroids of the Hartmann spots to the Ellipse fitting routine : True or False

    backgnd_sub : bool. apply background subtraction True or False
                  median_size = [1,15,15], gauss_sigma=[0,11,11] are used in filters to define the background

    cleaning    : bool. apply morphology.binary_opening to the map of significant pixels, or not.

    threshold = 'yen' = yen's method by defauLt (recommended)
                'mad' is equivalent to 'local' and means a local comparison with the mad
                    the comparison is using the parameters mad_sigma and mad_width, otherwise unused

    mad_sigma, mad_width : see 'threshold'

    verbose    : print infos or not

    skip_layer_0 : if True, the first layer of the cube is rejected from the analysis

    layer_selection : mutually exclusive with skip_layer_o
                      if not None, only the layers in layer_selection are kept for the analysis

    clean_pattern : True -> attempt to detect and reject labeled island not belonging to the hartmann pattern

    neighbour    : nth nearest neighbour used to reject the spurious islands from the true hartmann pattern

    OUTPUTS
    In this order:
     . all ellipse parameters fitted with method 1. Array of dimension [n,5] where n is the depth of the input cube
     . ibid for fitting method 2
     . Ellipse patch corresponding to the fit with method 1
     . ibid for fitting method 2
     . maps of significant pixels
     . maps of significant pixels after cleaning (= previous is cleaning=False)
     . maps of labels
     . background maps
    """
    import skimage
    import camtest.analysis.image_utils as iu
    from skimage import morphology
    import camtest.analysis.convenience as cv
    from skimage.measure import regionprops_table
    import scipy.ndimage as ndi
    import scipy.stats as scis

    NaN = float('nan')
    nan5 = np.array([NaN,NaN,NaN,NaN,NaN],dtype=float)

    # If single image was passed upon input, make it a cube for further convenience
    if len(cube.shape)==2:
        intercube = np.zeros([1,cube.shape[0],cube.shape[1]])
        print(intercube.shape, cube.shape)
        intercube[0,:,:] = cube
        cube = intercube
        del intercube

    if skip_layer_0:
        cube = cube[1:,:,:]
    elif layer_selection is not None:
        cube = cube[layer_selection,:,:]

    nlayers = cube.shape[0]

    if verbose: print(f"{skip_layer_0=}  --   {nlayers=}")

    # Background subtraction
    if verbose: print(f"Start background subtraction")

    backgroundMethod = 'filter'

    if median_size is None:
        median_size = [1,15,15]
    if gauss_sigma is None:
        gauss_sigma = [0,11,11]

    if backgnd_sub:
        cube, background = iu.backgroundSubtraction(np.array(cube,dtype=float),method=backgroundMethod,verbose=False, median_size=median_size, gauss_sigma=gauss_sigma)
    else:
        background = None

    # Thresholding for significant pixels
    if verbose: print(f"Start thresholding")

    # Global Yen Thresholding
    # significant[layer,:,:] = iu.significantPixels(cube[layer,:,:], method='yen')

    significant = np.zeros_like(cube)
    signiclean = np.zeros_like(cube)
    labels = np.zeros_like(cube,dtype=int)
    nlabels = np.zeros(nlayers,dtype=int)
    all_ellpars,all_ellparssci,all_ell,all_ellsci = [],[],[],[]

    for layer in range(nlayers):

        image = cube[layer,:,:]
        if threshold=='yen':
            yen = skimage.filters.threshold_yen(image)
            significant[layer,:,:][np.where(image >= yen)] = 1
        elif threshold=='mad' or threshold=='local':
            mad = ndi.generic_filter(image, scis.median_absolute_deviation, size=mad_width)
            significant[layer,:,:][np.where(image >= mad_sigma * mad)] = 1

        if cleaning:
            signiclean[layer,:,:] = iu.cleanSignificant(significant[layer,:,:], method='union')
        else:
            signiclean[layer,:,:] = significant[layer,:,:]

        # label works in 3D, but the connectivity is not restricted to the 'plane'
        # --> if used in 3D, labels could group pixels across images
        labels[layer,:,:] = morphology.label(signiclean[layer,:,:], background=0,connectivity=2)

        # Identify possible outliers wrt the hartmann pattern in the labeled islands
        # Remove them and re-number the remaining ones
        if clean_pattern:
            # Based on sigma-clipping. Here first neighbour is neighbour=1
            labels = cleanPattern(labels, neighbour=neighbour, nsigma=3, verbose=True)


        nlabels[layer] = np.max(labels)

        ilabels = [i for i in range(1, nlabels[layer] + 1)]
        slabels = [len(np.where(labels[layer,:,:] == n)[0]) for n in ilabels]
        if verbose:
            print(f"{layer=} Nb & sizes of the labelled regions : {nlabels[layer]} -- {slabels}")

        # B. FIT AN ELLIPSE TO THAT SET OF COORDINATES
        if nlabels[layer] >= 5:
            # At least 5 islands detected --> attempt to fit an ellipse
            skipped_fit = False

            try:
                sel = np.where(labels[layer,:,:] != 0)

                if centroiding:
                    ctable = regionprops_table(labels[layer,:,:], properties=('centroid', 'orientation'))
                    yclab, xclab = ctable["centroid-0"], ctable["centroid-1"]
                    ellipsin = np.vstack([xclab,yclab]).T
                else:
                    ellipsin = np.vstack(sel).T

                ellpars, ellipse = cv.fitEllipse(ellipsin)

                ellparssci, ellipsesci = cv.fitEllipseScikit(ellipsin)

            except:

                skipped_fit = True

        else:
            skipped_fit = True
            print(f"WARNING: {layer=}, nlabels {nlabels[layer]} < 5: skipping ellipse fit")

        if skipped_fit:
            ellpars, ellipse = nan5, None
            ellparssci, ellipsesci = nan5, None

        all_ellpars.append(ellpars)
        all_ellparssci.append(ellparssci)
        all_ell.append(ellipse)
        all_ellsci.append(ellipsesci)

    return np.array(all_ellpars), np.array(all_ellparssci), np.array(all_ell), np.array(all_ellsci), significant, signiclean, labels, background


def cleanPattern(labels, neighbour=2, nsigma=3, verbose=True):
    """

    INPUTS
    labels : numpy array [cube] resulting from  skimage.morphology.label
    neighbour : nth nearest neighbour used to compute the outlier score
    nsigma  : ~ sigma clipping on the score

    OUTPUT
    same as input 'labels'

    GOAL:
        identify and remove the islands that are not part of the hartmann pattern
        (e.g. groups of hot pixels associated to a dead column)
        Reject islands with a local outlier probability > threshold (~ 10 %)

    PRINCIPLE:
        Compute island centroids
        Compute the distance to the nth nearest neighbour for every island
        Exclude the extrema in distance (smallest & 2 largest)
        Establish a score = deviation from the mean (nth neighbour) distance between islands (expressed in sigma)
        Reject islands with a score > nsigma
    """
    from skimage.measure import regionprops_table
    from camtest.analysis import convenience as cv

    result = np.zeros_like(labels)

    nl = result.shape[0]

    if verbose:
        print()

    for ln in range(nl):
        labelimg = labels[ln,:,:]
        labelmax = np.max(labelimg)

        ctable = regionprops_table(labelimg, properties=('centroid', 'orientation'))
        yclab, xclab = ctable["centroid-0"], ctable["centroid-1"]

        score = patternOutliers(xclab,yclab,neighbour=neighbour,nsigma=nsigma)
        outliers = np.where(score > nsigma)[0]

        lnew = 0
        for linit in range(1,labelmax+1):
            if linit-1 in outliers:
                if verbose:
                    print(f'layer={ln} - Island {linit} --> outlier at {score[linit - 1]:7.2f} sigma')
            else:
                # print(f"{linit} --> {lnew+1}")
                result[ln,:,:][np.where(labelimg==linit)] = (lnew + 1)
                lnew += 1

    return result


def patternOutliers(x, y, neighbour=1, nsigma=3):
    """

    """
    from scipy.spatial.ckdtree import cKDTree

    # kd-tree for quick nearest-neighbour lookup.
    data = np.stack([x, y], axis=1)
    tree = cKDTree(data)

    # The distances of the datapoints to their k nearest neighbours and the
    # indices of their k nearest neighbours
    distance, contextSet = tree.query(data, neighbour+1)
    distance = distance[:,neighbour]
    distance_select = np.sort(distance)[1:-2]

    threshold = nsigma * np.std(distance_select)

    score = np.abs(distance-np.mean(distance_select)) / threshold

    return score

def plotHartmann(image, significant, signiclean, labels, fitmethod='pers', pltborder=6, vsigma=1, title=None, verbose=True, **kwargs):
    """
    plotHartmann(image,significant,signiclean,labels)

    image : original
    significant & signiclean : boolean maps (raw + cleaned with binary opening)
    labels : signiclean after labelling

    fitmethod : in ['pers', 'scikit']

    pltborder : nb of pixels displayed around the labelled regions

    vsigma = nb of std.dev used locally to define vmin,vmax (z-scale of the original image plot)

    **kwargs : are applied to the top left panel : original image

    """
    #patchellipse = matplotlib.patches.Ellipse((ellpars[1], ellpars[0]), width=2 * ellpars[2],height=2 * ellpars[3],
    #                                           angle=ellpars[4], color="r", fill=False, lw=2, ls=':', alpha=0.5)

    from camtest.analysis.convenience import fitEllipse,fitEllipseScikit
    from matplotlib import cm
    from skimage.measure import regionprops_table

    nlabels = int(np.max(labels))

    sel = np.where(labels != 0)
    ellipsin = np.vstack(sel).T

    xmin, xmax = np.min(sel[1]) - pltborder, np.max(sel[1]) + pltborder
    ymin, ymax = np.min(sel[0]) - pltborder, np.max(sel[0]) + pltborder

    imean, istd = np.mean(image[ymin:ymax,xmin:xmax]), np.std(image[ymin:ymax,xmin:xmax])
    vmin, vmax = imean - vsigma * istd, imean + vsigma * istd

    #vmin,vmax = np.min(image[xmin:xmax,ymin:ymax]) - 2000, np.max(image[xmin:xmax,ymin:ymax]) + 2000

    kwargs.setdefault('cmap', cm.hot)

    if fitmethod.find('pers')>=0:
        ellpars, ellipse = fitEllipse(ellipsin)
    elif fitmethod.find('sci')>=0:
        ellpars, ellipse = fitEllipseScikit(ellipsin)
    elif fitmethod.find('both')>=0:
        ellpars, ellipse = fitEllipse(ellipsin)
        ellpars2, ellipse2 = fitEllipseScikit(ellipsin)
        if verbose:
            print (f"Scikit fit {ellpars2}")

    if verbose:
            print (f"Pers fit   : {ellpars}")
            print (f"Image size : {image.shape}")

    fig, [[ax00, ax01], [ax02, ax03]] = plt.subplots(nrows=2, ncols=2, figsize=(12, 12), sharex=True, sharey=True)

    if title:
        plt.suptitle(title,fontsize=20)

    fontsize = 14
    ax00.imshow(image, interpolation='nearest', origin='lower', vmin=vmin, vmax=vmax, **kwargs)#, clim=(0, np.max(image) / 2.)
    ax00.set_title(f'Image', fontsize=fontsize)

    ax01.imshow(significant, cmap=plt.cm.gray, interpolation='nearest', origin='lower')
    ax01.set_title(f'significant', fontsize=fontsize)

    ax02.imshow(signiclean, cmap=plt.cm.gray, interpolation='nearest', origin='lower')
    ax02.set_title(f'Significant - Cleaned', fontsize=14)

    ax03.imshow(labels, cmap=plt.cm.nipy_spectral, interpolation='nearest', origin='lower', clim=(0., np.max(labels)))
    ax03.set_title(
        #f'Labels: {nlabels}\nEllipse [row,col]: [{ellpars[0] + rowpix1:6.1f},{ellpars[1] + colpix1:6.1f}]    [a,b]:[{ellpars[2]:5.1f},{ellpars[3]:5.1f}]',
        f'Labels: {nlabels}\nEllipse [row,col]: [{ellpars[0]:6.1f},{ellpars[1]:6.1f}]    [a,b]:[{ellpars[2]:5.1f},{ellpars[3]:5.1f}   alpha {ellpars[4]}:.2f]',
        fontsize=fontsize)

    ### Plot orientation problematic wrt the row/col display. It demands theta --> 90 - theta --> we re-establish 'ellipse'
    xc, yc, a, b, theta = ellpars
    ellipse = Ellipse((yc, xc), 2 * a, 2 * b, 90. - theta, edgecolor='r', facecolor='none', ls=':', lw=2)

    plt.gca().add_patch(ellipse)
    plt.plot([ellpars[1]], [ellpars[0]], ms=20, marker='+', c='w')

    if fitmethod.find('both')>=0:
        ### Plot orientation problematic wrt the row/col display. It demands theta --> 90 - theta --> we re-establish 'ellipse2'
        xc, yc, a, b, theta = ellpars2
        ellipse2 = Ellipse((yc, xc), 2 * a, 2 * b, 90. - theta, edgecolor='y', facecolor='none', ls='--', lw=1,alpha=0.5)

        plt.gca().add_patch(ellipse2)
        plt.plot([ellpars2[1]], [ellpars2[0]], ms=20, marker='x', c='y')

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    ctable = regionprops_table(labels, properties=('centroid', 'orientation'))
    yclab, xclab = ctable["centroid-0"], ctable["centroid-1"]
    plt.plot(xclab, yclab, ms=8, marker='+', c='w', ls="")

    return


def analysis_hartmann_cubes(filenames, sel_valid, nlayers=None, angles_in=None, outputdir=None, overwrite=False, verbose=True, skip_layer_0=True, layer_selection=None, postfix=None, cropwidth=200, setup=None):
    """
    Analyses all cubes in the fits files listed in 'filenames'

    Applies get_hartmann_ellipse to all of the files with predefined data-reduction parameters

    Writes the output in a one fits file named outputdir/obsid_{obsid}_ellipse_table.fits

    INPUT
    filenames = list of filenames. Expects full paths to _cube*fits

    sel_valid = selection of the valid filenames in the list
                e.g. fileanames = all cubes of an obsid, and cube 0 is empty
                     -> sel_valid = [i for i in range(len(filenames))] -> pop(0)

    angles_in = [n,2] array of boresight angle & azimuth from which the observation was defined
                if angles_in is given, the angles corresponding to the expected observed ccd-positions
                are computed incl. opt. distortion and the following fields are included in the resulting fits file:
                theta_in, phi_in = angles_in
                theta_comm, phi_comm, fpcoords_comm : computed by inverting the expected CCD locations of the source
                                                      [i.e. affected by the optical distortion]

    outputdir : directory where to write the results

    overwrite = False. Wheater to overwrite the output fits file if it pre-exists, or not.

    postfix = string that can be appended to the obsid name in the output file name

    cropwidth = size of mini-image cropped from the input cube around the approx location of every source.
               if None or negative: no cropping will be done.

    OUTPUT
    . one fits file named outputdir/obsid_{obsid}_ellipse_table.fits

    KNOWN FEATURE [now controlled with csl_5_layers: WILL SKIP THE FIRST LAYER IF THE NB OF LAYERS IN A CUBE IS FOUND = 5

    """
    from camtest import GlobalState
    from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates

    if setup is None:
        setup = GlobalState.setup

    fee_side = setup.camera.fee.ccd_sides.enum
    hcolstart = {fee_side.LEFT_SIDE.name:0, fee_side.RIGHT_SIDE.name:2255}
    minrowcol = 0
    maxcol = 2254
    maxrow = 4509

    # Nb of cubes to analyse
    ncubes = len(filenames)

    # Approximate source location on the CCD
    ccd_rows, ccd_cols, ccd_codes, ccd_sides = angles_to_ccd_coordinates(angles_in, distorted=True, verbose=False)

    # Historical parameter. In some early EM CSL data, due to some EGSE issue, the data structure was not constant
    # throughout a given hartmann dataset. The first layer had to be skipped whenever 5 layers were found (all data
    # were then aquired with 4 layers. This is kept here as a reminder, in case these old data must be re-reduced.
    csl_5_layers_issue = False

    # Extension number of the image cube
    extnc = 2

    if skip_layer_0:
        nlayers -= 1
    elif layer_selection is not None:
        nlayers = len(layer_selection)

    allepars = np.zeros([ncubes,nlayers,5],dtype=float)
    alleparssci = np.zeros_like(allepars)

    ccdids = np.zeros(ncubes,dtype=int)
    ccdsides = np.zeros(ncubes,dtype=str)
    rowstarts = np.zeros(ncubes,dtype=int)
    allbackgrounds = []
    allells, allellssci = [],[]

    if cropwidth is not None and cropwidth > 2:
        cropped = True
        crop_col_min = np.zeros(ncubes, dtype=int)
        crop_col_max = np.zeros(ncubes, dtype=int)
        crop_row_min = np.zeros(ncubes, dtype=int)
        crop_row_max = np.zeros(ncubes, dtype=int)
    else:
        cropped = False

    nan2d = np.array([[np.nan for i in range(5)] for j in range(nlayers)])

    for cn in range(ncubes):

        filename = filenames[cn]

        hduc = fits.open(filename)

        ccdids[cn] = hduc[2].header["CCD_ID"]
        ccdsides[cn] = hduc[2].header["SENSOR_SEL"][0]
        rowstarts[cn] = hduc[0].header["V_START"]
        # rowstarts[cn] = -hduc[2].header["CRPIX2"]
        # colstarts[cn] = -hduc[2].header["CRPIX1"]
        if hduc[0].header["V_START"] != -hduc[2].header["CRPIX2"]:
            print(f"WARNING {cn=} {hduc[0].header['V_START']=} {-hduc[2].header['CRPIX2']=}")

        sccd_meas = str(ccdids[cn])+ccdsides[cn]
        sccd_est  = str(ccd_codes[cn])+ccd_sides[cn]
        if sccd_meas != sccd_est:
            print(f"WARNING {cn=} CCD location {sccd_meas} != estimation: {sccd_est}")

        cube = np.array(hduc[extnc].data, dtype=float)

        if csl_5_layers_issue and cube.shape[0] == 5:
            print()
            print("WARNING ON CUBE SHAPE {cn} {cube.shape}")
            print()
            cube = cube[1:, :, :]

        if cn not in sel_valid:
            allepars[cn, :, :] = nan2d
            alleparssci[cn, :, :] = nan2d
            allbackgrounds.append(None)
            allells.append(None)
            allellssci.append(None)
            print()
            print(f"SKIPPING LAYER {cn}")
            print()
            continue

        est_row = int(np.round(ccd_rows[cn] - rowstarts[cn]))
        est_col = int(np.round(ccd_cols[cn] - hcolstart[ccd_sides[cn]]))
        if cropped:

            crop_row_min[cn] = max(est_row - cropwidth // 2, 0)
            crop_row_max[cn] = min(est_row + cropwidth // 2, 4510)
            crop_col_min[cn] = max(est_col - cropwidth // 2, 0)
            crop_col_max[cn] = min(est_col + cropwidth // 2, 2255)

            cube = cube[:, crop_row_min[cn]:crop_row_max[cn], crop_col_min[cn]:crop_col_max[cn]]

            """
            plt.figure(f"Cube_{cn}")
            plt.imshow(cube[3, :, :], cmap=matplotlib.cm.inferno, vmin=3500, vmax=6000, interpolation="nearest", origin="lower")
            plt.title(f"Cube {cn}")
            """

        print()
        print(f"Cube {cn:2d} : {filename}   {cube.shape}  CCD {ccdids[cn]}{ccdsides[cn]}  rowstart {rowstarts[cn]}")

        # get_hartmann_ellipse(cube, median_size=[1, 15, 15], gauss_sigma=[0, 11, 11], centroiding=True, cleaning=True, backgnd_sub=True, threshold='yen', mad_sigma=3, mad_width=15, verbose=True)
        epars, eparssci, ells, ellssci, significant, signiclean, labels, background = get_hartmann_ellipse(cube.copy(), skip_layer_0=skip_layer_0, layer_selection=layer_selection)

        allepars[cn, :, :] = epars
        alleparssci[cn, :, :] = eparssci
        allbackgrounds.append(background)
        allells.append(ells)
        allellssci.append(ellssci)

    # Note: cx is measleading here, cx it's "column", cy is "row"
    # cube[layer,row,column] = cube[layer, y, x] (given a pyplot where y runs vertically)
    cx, cy, ella, ellb, alpha = np.nanmean(allepars[:, :, 0], axis=1), np.nanmean(allepars[:, :, 1], axis=1), \
                                np.nanmean(allepars[:, :, 2], axis=1), np.nanmean(allepars[:, :, 3], axis=1), \
                                np.nanmean(allepars[:, :, 4], axis=1)
    cxsci, cysci, ellasci, ellbsci, alphasci =\
        np.nanmean(alleparssci[:, :, 0], axis=1), np.nanmean(alleparssci[:, :, 1], axis=1), \
        np.nanmean(alleparssci[:, :, 2], axis=1), np.nanmean(alleparssci[:, :, 3], axis=1), \
        np.nanmean(alleparssci[:, :, 4], axis=1)

    ellsize, ellsizesci = np.sqrt(ella * ella + ellb * ellb), np.sqrt(ellasci * ellasci + ellbsci * ellbsci)

    if verbose:
        print("Comparing 2 ellipse-fitting methods")
        print("Same center_x (tol e-4): ",np.allclose(cx, cxsci, equal_nan=True))  # ,atol=1.e-4)
        print("Same center_y (tol e-4): ",np.allclose(cy, cysci, equal_nan=True))  # ,atol=1.e-4)
        print("Same ell.size (tol e-1): ",np.allclose(ellsize, ellsizesci, equal_nan=True, atol=1.e-1))
        print("Diff. in ellipse-size: ",np.round(ellsize - ellsizesci, 4))

    # Reset the fitted center in the frame of the image
    if cropped:
        cx = cx + crop_col_min
        cy = cy + crop_row_min

    colstarts = np.array([hcolstart[i] for i in ccdsides])

    # Compute the fitted center in CCD coordinates
    cencol = cx + colstarts
    cenrow = cy + rowstarts

    # FP coords as measured  AND  COORDINATES OF THE CENTER OF ROTATION
    fpcoords_meas = np.array(
        [ccd_to_focal_plane_coordinates(crow, ccol, ccode) for crow, ccol, ccode in zip(cenrow, cencol, ccdids)])

    thetaphis_meas = np.array(
        [focal_plane_coordinates_to_angles(x, y) for (x, y) in zip(fpcoords_meas[:, 0], fpcoords_meas[:, 1])])
    thetas_meas, phis_meas = thetaphis_meas[:, 0], thetaphis_meas[:, 1]

    #
    # EXPORT THE RESULTS
    #

    outtab = Table()
    outtab["epars"] = allepars
    outtab["eparssci"] = alleparssci
    outtab["ccdid"] = ccdids
    outtab['ccdside'] = ccdsides
    outtab['rowstart'] = rowstarts
    outtab['cenx'] = cx
    outtab['ceny'] = cy
    outtab['cencol'] = cencol
    outtab['cenrow'] = cenrow
    outtab['ella'] = ella
    outtab['ellb'] = ellb
    outtab['ellsize'] = ellsize
    outtab['ellsizesci'] = ellsizesci
    outtab["fpcoords_meas"] = fpcoords_meas
    outtab["theta_meas"] = thetas_meas
    outtab["phi_meas"] = phis_meas

    if (angles_in is None):
        if verbose:
            print("No field angles provided upon input. Skipping comparison.")
            c = 0
            for tm, pm in zip(thetas_meas, phis_meas):
                print(f"{c:2d}   [{tm:6.3f}  {pm:8.3f}]")
                c += 1
    else:

        distorted = True

        ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles_in, distorted=distorted,
                                                                         verbose=verbose)

        fpcoords_comm = np.array([ccd_to_focal_plane_coordinates(crow, ccol, ccode) for crow, ccol, ccode in
                                  zip(ccdrows, ccdcols, ccdcodes)])

        angles_comm = np.array([focal_plane_coordinates_to_angles(xxfp, yyfp) for xxfp, yyfp in
                                zip(fpcoords_comm[:, 0], fpcoords_comm[:, 1])])

        thetas_comm = angles_comm[:,0]
        phis_comm   = angles_comm[:,1]
        fpcoords_comm = np.array([angles_to_focal_plane_coordinates(th,ph) for th,ph in zip(thetas_comm,phis_comm)])

        if verbose:
            print("Field angles provided upon input. Comparison:")
            print("  theta [meas comm]   phi [meas comm]")
            c = 0
            for tm, tc, pm, pc in zip(thetas_meas, thetas_comm, phis_meas, phis_comm):
                print(f"{c:2d}   [{tm:6.3f}  {tc:6.3f}]   [{pm:8.3f}  {pc:8.3f}]")
                c += 1

        # Systematic in delta_phi ?
        delta_phis = phis_meas - phis_comm
        cv.stats(delta_phis[sel_valid])

        delta_thetas = thetas_meas - thetas_comm
        cv.stats(delta_thetas[sel_valid])

        outtab["theta_in"] = angles_in[:,0]
        outtab["phi_in"] = angles_in[:,1]
        outtab["theta_comm"] = thetas_comm
        outtab["phi_comm"] = phis_comm
        outtab["fpcoords_comm"] = fpcoords_comm
        outtab["delta_phi"] = delta_phis
        outtab["delta_theta"] = delta_thetas

    sobsid = hduc[0].header["OBSID"]

    if not postfix:
        outputfile = outputdir + f"/obsid_{sobsid}_ellipse_table.fits"
    else:
        outputfile = outputdir + f"/obsid_{sobsid}_ellipse_table{postfix}.fits"

    if verbose:
        print(f"Output file : {outputfile}")
        print("Columns", outtab.colnames)

    outtab.write(outputfile, overwrite=overwrite)

    return outtab


def rxry_to_flat(phis, ellsizes, guesspars=[0.5, 0.5, 29.6], radiusmm=36., mmperpix=0.065, verbose=True):
    """
    Pass phis, ellipse size & radius in mm
    Fit a sinewave to the curve ellipse size vs phis
    Computes the amplitude of the RxRy rotations to apply to the
    plane of measurement in order to flatten the relation ellsize = f(phis)
    It is assumed that all of the input measures were acquired at the same boresight angle (elevation)
    i.e. the same radius in focal-plane coordinates

    phis : input azimuths
    ellsizes : input ellipse sizes
    guesspars : input parameters for the sinewave fit
    radiusmm  : radius of the circle at which all measurements were obtained, in mm
                 3.1 deg -> 13.25 mm
                 8.3 deg -> 36.00 mm
                12.4 deg -> 54.50 mm
                16.3 deg -> 73.60 mm
    mmperpix = millimeters of defocussing / pixel of change in the measured hartmann ellipse size
               60 - 65 microns / pixel
    """
    from scipy.optimize import curve_fit
    def cosine_funcfixf(x, amplitude, phase, offset):
        return np.cos(x * 2. * np.pi / 360. + phase) * amplitude + offset

    xin = phis
    yin = ellsizes
    fitf = curve_fit(cosine_funcfixf, xin, yin, p0=guesspars)

    amp, phase, offset = fitf[0]

    if amp > 0:
        phimax = -phase
    else:
        phimax = -phase + np.pi

    ampmm = abs(amp) * mmperpix

    gamma = np.arctan(ampmm / radiusmm)

    rx = -1. * np.arcsin(np.sin(gamma) * np.sin(phimax))
    ry = -1. * np.arctan(-np.tan(gamma) * np.cos(phimax))

    rx, ry = np.rad2deg(rx), np.rad2deg(ry)

    # Coordinates of the normal to the plane:
    normal = [-np.sin(gamma)*np.cos(phimax), -np.sin(gamma)*np.sin(phimax), np.cos(gamma)]

    # This is == gamma !      NB: normal_tilt in arcmin, gamma in radians
    normal_tilt = np.rad2deg(np.arccos(np.cos(normal[0])*np.cos(normal[1])))*60.

    if verbose:
        print(f"{amp=:.3f} {ampmm=:.3f} {phase:.4f} {offset:.3f} - phimax {np.rad2deg(phimax):.3f} deg - "
              f"gamma={np.rad2deg(gamma):.3f} deg - rx ry : {rx:.4f} {ry:.4f} - normal : [{normal[0]:.3e}, {normal[1]:.3e}, "
              f"{normal[2]:.3e}] - tilt_angle : {normal_tilt:.3f} arcmin")

    return rx, ry, normal, normal_tilt, phimax, gamma, fitf[0]


def analysis_single_cube(obsid, datadir="/data/CSL/obs/", verbose=True, show_layer=None, ref_size=0., layer_selection=None, theta=None):
    """
    analysis_single_cube(obsid, datadir="/data/CSL/obs/", verbose=True, show_layer=None, ref_size=0., layer_selection=None, theta=None)

    INPUT
    obsid   : integer
    datadir : directory of the input data
    show_layer : int. If not None, displays the image, the significant pixel map, the label map and the fittted ellipse.

    ref_size : size of a the ellipse in a reference measurement. The size here will be compared to that one, in pixels and in microns
    layer_selection : tuple of layers to reduce
    theta : boresight angle of the observation, only used to derive the conversion between hartmann size and defocus in microns
    """

    # Microns of defocus / pixel in measured ellipse-size (65 = value at 8 deg from the optical axis.)
    if theta is None:
        theta = 8.3
    microns_per_pixel = get_tau(theta, setup=None)

    sobsid = str(obsid).zfill(5)

    try:
        print("PFM - FM")
        obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
        filenames = cv.fileSelect([f'{sobsid}_','cube', 'fits'], location=datadir + obsidir)
        ffilenames = [datadir+obsidir+filename for filename in filenames]
    except:
        print("EM")
        filenames = cv.fileSelect([f'{sobsid}_','cube', 'fits'], location=datadir)
        ffilenames = [datadir+filename for filename in filenames]

    for f in ffilenames:
        print(f)

    if len(ffilenames) > 1:
        print("WARNING : Multiple cubes found:")
        for i in filenames:
            print(i)
        print("ONLY REDUCING THE FIRST ONE: ffilenames[0]")

    filename = ffilenames[0]

    if verbose: print(f"Reducing file : {filename}")

    hduc = fits.open(filename)
    cube = np.array(hduc[2].data, dtype=float)

    epars, eparssci, ells, ellssci, significant, signiclean, labels, bgnd = get_hartmann_ellipse(cube.copy(), layer_selection=layer_selection)

    ellsize = np.sqrt(pow(epars[:, 2], 2) + pow(epars[:, 3], 2))
    ellsizesci = np.sqrt(pow(eparssci[:, 2], 2) + pow(eparssci[:, 3], 2))

    if verbose:
        avg_size = np.nanmean(ellsizesci)
        std_size = np.nanstd(ellsizesci)
        print(cube.shape)
        print(f"Difference in ellipse size between fit. methods: {ellsize - ellsizesci}")
        print(f"Fitting methods give the same ellipse size     : {np.allclose(ellsize - ellsizesci, 0., atol=1.e-2)}")
        print(f"{obsid=}   Ellipse sizes                   : {ellsizesci}")
        print(f"{obsid=}   Ellipse sizes - Avg Ellipse size: {ellsizesci-avg_size} [pix] = {(ellsizesci-avg_size)*microns_per_pixel} [microns]")
        print()
        print(f"{obsid=}   Avg ellipse size : {avg_size:.3f} +- {std_size:.3f}   Diff with reference {(avg_size - ref_size):.3f} [pix]  =  {((avg_size - ref_size) * microns_per_pixel):.2f} +- {(std_size * microns_per_pixel):.2f} [microns]")
        print()

    if show_layer is not None:
        plotHartmann(cube[show_layer,:,:].copy(), significant[show_layer,:,:], signiclean[show_layer,:,:],
                     labels[show_layer,:,:], fitmethod='pers', pltborder=6, vsigma=1, title=None, verbose=verbose)

    return ellsizesci


def hartmann_reduction(obsid, nlayers=5, layer_selection=None, cube_selection=None, fov_angles=None,
                       datadir="/data/CSL/obs/", outputdir="/data/CSL/reduced/", cropwidth=200, verbose=True):
    """
    INPUT
    obsid   : integer

    nlayers=5 : nb of layers in every cube

    layer_selection=None : selection of layers to be reduced

    cube_selection=None : selection of cubes to be reduced. The selection order must correspond to
                          the list of fits files (1 / cube) found  for the input obsid

    fov_angles : Requested fov_angles (i.e. undistorted). These are only used compute the input focal plane
                 coordinates and save them along the measured ones, for the sake of completeness.

    datadir : directory of the input data, e.g. /data/CSL/obs/

    outputdir : directory where the reduction results are written, e.g. /data/CSL/reduced/

    cropwidth : size of the box to crop around the estimated location of the source in the image
                to limit the problems with cosmetic defects and accelerate the reduction

    verbose : info and debug prints
    """
    from camtest.analysis.functions.hartmann_utils import analysis_hartmann_cubes

    skip_layer_0 = False
    postfix = None
    overwrite = True

    sobsid = str(obsid).zfill(5)

    try:
        print("PFM - FM")
        obsidir = cv.fileSelect([f'{sobsid}'], location=datadir)[0] + '/'
        filenames = cv.fileSelect([f'{sobsid}_','cube', 'fits'], location=datadir + obsidir)
        ffilenames = [datadir+obsidir+filename for filename in sorted(filenames)]
    except:
        print("EM")
        filenames = cv.fileSelect([f'{sobsid}_','cube', 'fits'], location=datadir)
        ffilenames = [datadir+filename for filename in sorted(filenames)]

    if verbose:
        for f in ffilenames:
            print(f)

    if cube_selection is None:
        cube_selection = [i for i in range(len(ffilenames))]

    ctab = analysis_hartmann_cubes(filenames=ffilenames, sel_valid=cube_selection, nlayers=nlayers,
                                   angles_in=fov_angles,
                                   outputdir=outputdir, overwrite=overwrite, verbose=True, skip_layer_0=skip_layer_0,
                                   layer_selection=layer_selection, postfix=postfix, cropwidth=cropwidth)

    return ctab


def hartmann_analysis_circle(obsids, tau=None, datadir="/Volumes/IZAR/plato/data/reduced/", figname=None, verbose=True, radiusmm=None, setup=None, n_sigma=None, meas_error=None, png_dir=None):
    """
    hartmann_analysis_circle(obsids, tau=None, datadir="/Volumes/IZAR/plato/data/reduced/", figname=None, verbose=True, radiusmm=None, setup=None, n_sigma=None, meas_error=None, png_dir=None)

    SYNOPSIS
    . Read in fits files reduced with hartmann_reduce
    . Compares the average size of the hartmann pattern (ellipse) found in all of the obsids with the first one.
    . Plots the ellipse size as a function of the azimuth of all obsids together.
    . Returns a suggested filename to save the plot when ready.
    The measurement site of every obsid and the label to mark them in the plot can be given on input.

    INPUT
    obsids : the list of obsids to analyse.
             obsids can be passed in two different shapes:
                . a simple list or array : [100, 200, 300]. The measurement site is taken from Globalstate.Setup
                . a (n x 3) list or array where every element contains [obsid, site, label], e.g.
                        obsids = []
                        obsids.append([900, "CSL", "CSL Final"])
                        obsids.append([2088, "SRON", "SRON EM1 Start"])
            In all cases the first obsid in the list will be used as a reference for comparison with
             all the other ones.

    tau=None : the assumed change of focus wrt the measured size of the Hartmann pattern (ellipse) [microns / pixel]
               (theta=8.3 -> tau=65 microns/pix)

    datadir : location of the fits files with the reduction parameters of all obsids (produced by "hartmann reduction")

    figname : passed to matplotlib.pyplot. Allowing to append the plot produced here to a pre-existing one.

    verbose : prints information and diagnostic numbers from the analysis

    radiusmm : radius of the circle, in mm on the focal plane (theta=8.3 -> 36 mm).
               Used for the sine-fit performed in the tilt estimate.

    n_sigma  : tolerance factor (wrt "meas_error") for the verification of the
               alignment criteria (global & local comparisons between datasets)

    meas_error : uncertainty on each individual 'hartmann size'
                 if None or negative, the standard deviation of all measurements is considered

    OUTPUT
    String: proposed name to save the plot

    EXAMPLE
    obsids = [100, 200, 300]
    plotname = hartmann_analysis_circle(obsids, datadir=reduceddir, figname="MyFigure", verbose=True)
    plt.savefig(mydirectory + plotname)

    """

    alpha=1
    fontsize = 14

    orange = (1., 0.75, 0.)
    gray = (0.5, 0.5, 0.5)
    pink = (1., 0.5, 0.75)
    lightgray = (0.75, 0.75, 0.75)
    lightgreen = (0.5, 1, 0.5)
    lightblue = (0.5, 0.5, 1.0)
    colors = ['k', 'r', 'g', orange, 'b', lightblue, 'c', 'm', gray, lightgray, lightgreen, pink]

    if setup is None:
        setup = load_setup()

    if n_sigma is None:
        n_sigma = 3

    # Format Input --> obsids, sites, plot_labels

    obsids = np.array(obsids)
    nobs = obsids.shape[0]

    if len(obsids.shape) == 1:
        site = setup.site_id
        sites = [site for i in obsids]
        labels = ["" for i in obsids]
        #outlierss = [[] for i in range(nobs)]
    elif obsids.shape[1]==2:
        sites = [obsids[i, 1] for i in range(nobs)]
        labels = ["" for i in obsids]
        obsids = [int(obsids[i, 0]) for i in range(nobs)]
        #outlierss = [[] for i in range(nobs)]
    elif obsids.shape[1]==3:
        sites = [obsids[i, 1] for i in range(nobs)]
        labels =[" " + obsids[i, 2] for i in range(nobs)]
        obsids = [int(obsids[i, 0]) for i in range(nobs)]
        #outlierss = [[] for i in range(nobs)]
    # elif obsids.shape[1] == 4:
    #     sites = [obsids[i, 1] for i in range(nobs)]
    #     labels = [" " + obsids[i, 2] for i in range(nobs)]
    #     obsids = [int(obsids[i, 0]) for i in range(nobs)]
    #     outlierss = [obsids[i,3] for i in range(nobs)]
    else:
        print("WARNING: Structure of input 'obsids' unclear. {obsids.shape=}")


    # - - - - - - -
    hashok={True:"OK", False:"NOT OK"}

    outputstring = ""
    c = -1
    for obsid, site, label in zip(obsids, sites, labels):
        c += 1

        # LOAD THE DATA

        sobsid = str(obsid).zfill(5)

        # if verbose:
        #     print(f"{sobsid} {site} {label=:20s} ")

        filenames = cv.fileSelect([f'{sobsid}_', site, 'fits'],location=datadir)
        if len(filenames)==1:
            filename = filenames[0]
        else:
            print(f"ERROR: {obsid=} No, or multiple files found: {filenames=}")
            raise Exception("INPUT file not found or not unique.")

        cfits = fits.open(Path(datadir) / filename)
        ctab  = Table(cfits[1].data)

        sel = np.where(np.isfinite(ctab['ellsizesci']))
        if tau is None:
            tau = get_tau(elevation=np.nanmean(ctab["theta_meas"][sel]), setup=setup)

        if radiusmm is None:
            radiusmm = np.nanmean(ctab["theta_meas"][sel]) * 3600 / 15 * 0.018

        # COMPARISON

        if c==0:
            ref,oref = ctab, obsid

            outputstring = circle_center(ctab=ref, obsid=obsid, site=site, resultstring=outputstring, png_dir=png_dir, setup=setup, verbose=False)

            outputstring += f"{sobsid} {site:5s} {label=:20s}    avg +- std : {np.nanmean(ref['ellsizesci']):7.3f} +- {np.nanstd(ref['ellsizesci']):7.3f} [pixels]\n"


        else:
            meas, omeas = ctab, obsid

            outputstring = circle_center(ctab=meas, obsid=obsid, site=site, resultstring=outputstring, png_dir=png_dir, setup=setup, verbose=False)

            compare = (meas['ellsizesci'] - ref['ellsizesci']) * tau

            # Verify match according to established global and local criteria

            max_offset = setup.camera.fpa.max_offset
            if (meas_error is None) or (meas_error < 0.):
                meas_error = np.nanstd(compare)

            # max_offset = dSigma_max in the formulae

            print(f"{meas_error=} {tau=} {n_sigma=} {max_offset=} {len(compare)=}")
            tolerance_global = (max_offset + n_sigma * np.sqrt(2.) * meas_error / np.sqrt(len(compare)))
            criterion_global = np.abs(np.nanmean(compare)) < tolerance_global
            match_global = hashok[criterion_global]

            tolerance_local = (max_offset + n_sigma * np.sqrt(2.) * meas_error)
            criterion_local = np.max(np.abs(compare)) < tolerance_local
            match_local = hashok[criterion_local]

            # if verbose:
            #     print()
            #     print(f"{sobsid} {site:5s} {label=:20s}    {omeas} - {oref} : {np.nanmean(compare):7.3f} +- {np.nanstd(compare):7.3f}  [microns]")
            #     #cv.stats((ref['ellsizesci'] - meas['ellsizesci']) * tau)

            outputstring += f"{sobsid} {site:5s} {label=:20s}    {omeas} - {oref} : {np.nanmean(compare):7.3f} +- {np.nanstd(compare):7.3f}  [microns]\n"
            outputstring += " "*12 + f"Match Global {np.abs(np.nanmean(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {meas_error:5.2f} / sqrt({len(compare)}) = {tolerance_global:6.2f} : {match_global}\n"
            outputstring += " "*12 + f"Match Local  {np.max(np.abs(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {meas_error:5.2f} = {tolerance_local:6.2f}            : {match_local}\n"

        # TILT ESTIMATE

        try:

            sel = np.where(np.isfinite(ctab['ellsizesci']))
            fitx, fity_in = ctab['phi_meas'][sel], ctab['ellsizesci'][sel]
            guesssize = np.mean(fity_in)
            rxhm, ryhm, normalhm, tilthm, pmaxhm, gammhm, parsm = rxry_to_flat(fitx,fity_in, guesspars=[0.5, 0.5, guesssize],
                                                                               radiusmm=radiusmm, mmperpix=tau/1000.,
                                                                               verbose=False)
            if pmaxhm > np.pi: pmaxhm = pmaxhm - (2*np.pi)
            # # print("Sine fit to cancel the tilt:")
            # # print(" "*12 + f"Tilt : {tilthm:7.3f} arcmin") #= {np.rad2deg(gammhm) * 60:7.3f}")
            # # print(" "*12 + f"To make it flat --> [Rx, Ry] : [{rxhm:7.3f},{ryhm:7.3f}]")
            # # print("     Fit params [ampl, phase, offset]:", parsm)

            # print(" "*12 + f"Tilt:  {tilthm:7.3f} arcmin. To make it flat --> [Rx, Ry] : [{rxhm:7.3f},{ryhm:7.3f}]")
            outputstring += " "*12 + f"Tilt:  {tilthm:7.3f} arcmin. To make it flat --> [Rx, Ry] : [{rxhm:7.3f},{ryhm:7.3f}]  phi_of_max {np.rad2deg(pmaxhm):7.2f} deg\n\n"
            plotfit = True
        except:
            # print("Sine fit to cancel the tilt: did not converge")
            plotfit = False
            outputstring += "Sine fit to cancel the tilt: did not converge\n\n"

        # PLOT

        if verbose:
            plt.figure(figname)
            if c==0:
                plt.plot(ctab['phi_meas'], ctab['ellsizesci'], c=colors[c % len(colors)], alpha=1, marker='o', ls='-',
                         lw=2, label=f"{obsid}_{site}: {label}")
                plt.grid(alpha=0.25)
                plt.legend()
                plt.xlabel("Azimuth $[^\circ]$", size=fontsize + 5)
                plt.ylabel("Ellipse size [pix]", size=fontsize + 5)
                plt.title(f"Ellipse size vs azimuth", size=fontsize + 5)
                plotname = f"hartmann_ell_vs_azimuth_obsid_{sobsid}"

            else:
                plt.plot(ctab['phi_meas'],ctab['ellsizesci'],c=colors[c%len(colors)],alpha=alpha,marker='o',ls='--',label=f"{obsid}_{site}: {label}")
                plt.legend()
                plotname += f"_{sobsid}"

            if plotfit:
                fity_out = cosine_funcfixf(fitx, *parsm)
                plt.plot(fitx, fity_out, c=colors[c % len(colors)], alpha=0.25, marker='', ls='--')
        else:
            plotname = "noplot"

    if verbose:
        print(outputstring, flush=True)

    return plotname+".png", outputstring

def circle_center(ctab, obsid, site, resultstring="", png_dir=None, setup=None, verbose=False):
    """
    Fits a circle to the measured hartmann positions & displays the stats on the differences with the expected positions
    """
    import camtest.analysis.functions.fov_utils as fovu

    sobsid = str(obsid).zfill(5)

    if setup is None:
        setup = load_setup()

    try:
        fpcoords_comm = ctab["fpcoords_comm"]
        fpcoords_meas = ctab["fpcoords_meas"]
        thetas_comm, phi_comm = ctab["theta_comm"], ctab["phi_comm"]
        thetas_meas, phi_meas = ctab["theta_meas"], ctab["phi_meas"]
    except:
        print("CRITICAL: the input fits table doesn't contain the expected fields")
        print(ctab.colnames)
        raise ValueError

    if verbose:
        for thec, them, phic, phim in zip(thetas_comm, thetas_meas, phi_comm, phi_meas):
            print(f"[{them:8.3f},{thec:8.3f}] dtheta: {them - thec:8.3f}   |   [{phim:8.3f},{phic:8.3f}]   dphi: {phim - phic:8.3f}")

    dtheta = thetas_meas - thetas_comm
    dphi = phi_meas - phi_comm

    if png_dir is not None:
        plt.ioff()
        plt.figure(f"dphi_{obsid}")
        plt.plot(phi_comm, dtheta, 'k.-', label=r"$\delta\theta$")
        plt.plot(phi_comm, dphi, 'r.-', label=r"$\delta\phi$")
        plt.title(f"obsid {obsid} measured-commanded positions", size=15)
        plt.xlabel("Azimuth [deg]", size=15)
        plt.ylabel(r"$\Delta$ [deg]", size=15)
        plt.grid(alpha=0.25)
        plt.legend(fontsize=20)
        plt.savefig(png_dir + f"obsid_{sobsid}_{site}_measured-commanded_positions_circle.png")

    try:
        pars_comm, circle_comm = cv.fitCircle(fpcoords_comm)
        cenx_comm, ceny_comm, radius_comm = pars_comm

        pars_meas, circle_meas = cv.fitCircle(fpcoords_meas)
        cenx_meas, ceny_meas, radius_meas = pars_meas

        decenter = np.sqrt(cenx_meas * cenx_meas + ceny_meas * ceny_meas)

        resultstring += f"{sobsid} {site:5s} Center: commanded: [{cenx_comm:7.3f}, {ceny_comm:7.3f}] measured: [{cenx_meas:7.3f}, {ceny_meas:7.3f}] -- {decenter=:.3f} mm\n"
        resultstring += f"{' '*19} delta_phi modulation. Expected {np.rad2deg(np.arctan(decenter / radius_meas)) * 2:.3f}, measured: {(np.max(dphi) - np.min(dphi)):.3f} deg peak-to-peak\n"

        if png_dir is not None:
            fovu.plotCCDs(figname=f"FoV_{obsid}", setup=setup)
            plt.plot(fpcoords_comm[:, 0], fpcoords_comm[:, 1], 'ko', label="Comm")
            plt.plot(fpcoords_meas[:, 0], fpcoords_meas[:, 1], 'ro', label="Meas")
            plt.plot([cenx_comm], [ceny_comm], 'k+', ms=20)
            plt.plot([cenx_meas], [ceny_meas], 'rx', ms=20)
            plt.legend(fontsize=14)
            plt.title(f"{obsid=}_{site}", size=20)
            plt.savefig(png_dir + f"obsid_{sobsid}_{site}_fov_comm_vs_meas_positions.png")
            plt.ion()

    except:
        print(f"{sobsid} {site:5s} Fitting a circle to the hartmann positions did not converge")
        resultstring += f"{sobsid} {site:5s} Fitting a circle to the hartmann positions did not converge\n"

    return resultstring


def hartmann_analysis_full(obsids, n_thetas=4, datadir="/Volumes/IZAR/plato/data/reduced/", maxsize=100, figname=None, setup=None, n_sigma=None, meas_error=None, verbose=True):
    """
    hartmann_analysis_full(obsids, n_thetas=4, datadir="/Volumes/IZAR/plato/data/reduced/", maxsize=100, figname=None, setup=None, n_sigma=None, meas_error=None, verbose=True)

    SYNOPSIS
    . Read in fits files reduced with hartmann_reduce
    . Compares the average size of the hartmann pattern (ellipse) found in all of the obsids with the first one.
    . Plots the ellipse size as a function of the azimuth of all obsids together.
    . Returns a suggested filename to save the plot when ready.
    The measurement site of every obsid and the label to mark them in the plot can be given on input.

    INPUT
    obsids : the obsid to analyse, or the two obsids to analyse.
             obsids can be passed in two different shapes:
                . a simple list or array : [100, 200, 300]. The measurement site is taken from Globalstate.Setup
                . a (2 x 3) list or array where every element contains [obsid, site, label], e.g.
                        obsids = []
                        obsids.append([842, "CSL", "CSL Post Bolting"])
                        obsids.append([2242, "SRON", "SRON EM1 Start"])
            In all cases the first obsid in the list will be used as a reference for comparison with the other ones.

    n_thetas : the measures are grouped by elevation angle. This is done via a clustering algorith. This parameter
               specifies how many groups of theta are present in the data (40 fov positions : 4; 76 fov positions : 6)

    datadir : location of the fits files with the reduction parameters of all obsids (produced by "hartmann reduction")

    maxsize : hartmann patterns with size > maxsize are considered invalid and disregarded for the analysis

    figname : passed to matplotlib.pyplot. Allowing to append the plot produced here to a pre-existing one.

    setup : a setup. If None, GlobalState.setup is used.

    n_sigma  : tolerance factor (wrt "meas_error") for the verification of the
               alignment criteria (global & local comparisons between datasets)

    meas_error : uncertainty on each individual 'hartmann size'
                 if None or negative, the standard deviation of all measurements is considered

    verbose : prints information and diagnostic numbers from the analysis

    OUTPUT
    String: proposed name to save the plot

    Remarks
        "tau" : the assumed change of focus wrt the measured size of the Hartmann pattern (ellipse) [microns / pixel]
        taus is read from the setup table setup.camera.fov.tau which is a list of 2 lists : the elevation angles and the
        values of tau


    EXAMPLE
    obsids = []
    obsids.append([842, 'CSL', "CSL Post-Bolt"])
    obsids.append([642, 'CSL', "CSL Pre-Bolt"])
    plotname = hartmann_analysis_full(obsids, n_thetas=4, datadir="/Volumes/IZAR/plato/data/reduced/", maxsize=100,
                                      figname="MyPlot, setup=None, verbose=True)
    plt.savefig(mydirectory + plotname)

    """
    from camtest import GlobalState

    fontsize = 14

    # Maximum difference in elevation to accept that 2 measurements match (can be compared)
    max_dtheta = 0.5
    # Ibid. in azimuth
    max_dphi = 5.

    orange = (1., 0.75, 0.)
    gray = (0.5, 0.5, 0.5)
    pink = (1., 0.5, 0.75)
    lightgray = (0.75, 0.75, 0.75)
    lightgreen = (0.5, 1, 0.5)
    lightblue = (0.5, 0.5, 1.0)
    colors = ['k', 'r', 'g', 'b', gray, lightblue, lightgreen, pink, lightgray, orange, 'c', 'm']

    if setup is None:
        setup = GlobalState.setup

    max_offset = setup.camera.fpa.max_offset

    # Format Input --> obsids, sites, plot_labels
    obsids = np.array(obsids)
    nobs = obsids.shape[0]

    if len(obsids.shape) == 1:
        from camtest import GlobalState
        site = GlobalState.setup.site_id
        sites = [site for i in obsids]
        labels = ["" for i in obsids]
    elif obsids.shape[1]==2:
        sites = [obsids[i, 1] for i in range(nobs)]
        labels = ["" for i in obsids]
        obsids = [int(obsids[i, 0]) for i in range(nobs)]
    elif obsids.shape[1]==3:
        sites = [obsids[i, 1] for i in range(nobs)]
        labels =[" " + obsids[i, 2] for i in range(nobs)]
        obsids = [int(obsids[i, 0]) for i in range(nobs)]
    else:
        print("WARNING: Structure of input 'obsids' unclear. {obsids.shape=}")


    # - - - - - - -
    hashok={True:"OK", False:"NOT OK"}

    outputstring = ""
    c = -1
    for obsid, site, label in zip(obsids, sites, labels):
        c += 1

        # LOAD THE DATA

        sobsid = str(obsid).zfill(5)

        filenames = cv.fileSelect([f'{sobsid}_', site, 'fits'],location=datadir)
        if len(filenames)==1:
            filename = filenames[0]
        elif len(filenames)==0:
            print(f"ERROR: {obsid=} no file found: {filenames=}")
        else:
            print(f"WARNING: {obsid=} multiple files found: {filenames=}")
            print(f"WARNING: {obsid=} processing the first: {filenames[0]}")
            filename = filenames[0]

        cfits = fits.open(str(datadir+filename))
        ctab  = Table(cfits[1].data)

        # Conversion to Pandas
        coltopandas = ctab.colnames
        # Pandas can't accomodate multi-column fields
        # LDO data reduction doesn't have those fields
        if site != "LDO":
            coltopandas.remove('epars')
            coltopandas.remove('eparssci')
            coltopandas.remove('fpcoords_meas')
            coltopandas.remove('fpcoords_comm')

        cpan = ctab[coltopandas].to_pandas()

        # COMPARISON

        if c==0:
            ref,oref = cpan, obsid

            # Selection of measurements smaller than maximum ellipse size (basic outlier rejection)
            selref = np.where(ref['ellsizesci'] <= maxsize)[0]
            refall = ref.iloc[selref]

            # Measurements < maxsize
            refthetasok = np.array(ref.theta_meas.iloc[selref], dtype=float)
            # Clustering the measurements by boresight angle theta
            # rfthetasmeans   = average boresight of every cluster
            # refthetaslabels = cluster label of every measurement
            # refulabels      = unique set of labels = range(n_thetas)
            # refsulabels     = set of labels, sorted by increasing boresight angle
            # refsthetasmeans = average boresight angle theta, sorted by increasing value
            refthetasmeans, refthetaslabels = cv.cluster1D(refthetasok, n_clusters=n_thetas)
            refulabels = np.unique(refthetaslabels)
            refsulabels = refulabels[np.argsort(refthetasmeans)]
            refsthetasmeans = np.sort(refthetasmeans)

            # print(f">maxsize: {np.where(ref['ellsizesci'] > maxsize)}")
            # print(f"{refall=}")
            # print(f"{refthetasok=}")
            # print(f"{refthetasmeans=}")
            # print(f"{refthetaslabels=}")
            # print(f"{refulabels=}")
            # print(f"{refsulabels=}")
            # print(f"{refsthetasmeans=}")

            if verbose:
                plt.figure(figname, figsize=(10,12))

            for ul,uth in zip(refsulabels, refsthetasmeans):

                # Stats
                selul = np.where(refthetaslabels==ul)
                outputstring += f"{sobsid} {site:5s}  {label=:20s} | {ul=:2d} elevation {uth:6.2f}, {len(selul[0]):3d} meas, avg +- std : {np.nanmean(refall['ellsizesci'].iloc[selul]):7.3f} +- {np.nanstd(refall['ellsizesci'].iloc[selul]):7.3f} [pixels]\n"

                isort = np.argsort(np.array(refall.phi_meas.iloc[selul]))
                tmp = np.array(refall.ellsizesci.iloc[selul])
                refsize = tmp[isort]
                refphi = np.sort(np.array(refall.phi_meas.iloc[selul]))

                # Tilt fit
                plotfit = False
                try:

                    tau = get_tau(uth, setup=setup)
                    radiusmm = np.nanmean(uth) * 3600 / 15 * 0.018

                    # fitx, fity_in = refall.phi_meas.iloc[selul], refall.ellsizesci.iloc[selul]
                    fitx, fity_in = refphi, refsize
                    guesssize = np.nanmean(fity_in)
                    rxhm, ryhm, normalhm, tilthm, pmaxhm, gammhm, parsm = rxry_to_flat(fitx, fity_in,
                                                                                       guesspars=[0.5, 0.5, guesssize],
                                                                                       radiusmm=radiusmm,
                                                                                       mmperpix=tau / 1000.,
                                                                                       verbose=False)
                    if pmaxhm > np.pi: pmaxhm = pmaxhm - (2 * np.pi)
                    outputstring += " " * 12 + f"Tilt:  {tilthm:7.3f} arcmin. To make it flat --> [Rx, Ry] : [{rxhm:7.3f},{ryhm:7.3f}]  phi_of_max {np.rad2deg(pmaxhm):7.2f} deg\n"
                    plotfit = True
                except:
                    outputstring += "Sine fit to cancel the tilt: did not converge\n"

                # Plot
                if verbose:

                    # plt.plot(refall.phi_meas.iloc[selul], refall.ellsizesci.iloc[selul], c=colors[c % len(colors)], marker='o', ls='-', label=label+f" {uth:3.0f}")
                    plt.plot(refphi, refsize, c=colors[c % len(colors)], marker='o', ls='-', label=label+f" {uth:3.0f}")

                    if plotfit:
                        fity_out = cosine_funcfixf(fitx, *parsm)
                        plt.plot(fitx, fity_out, c=colors[c % len(colors)], alpha=0.25, marker='', ls='--')

            if verbose:
                plt.grid(alpha=0.25)
                plt.legend()
                plt.xlabel("Azimuth $[^\circ]$", size=fontsize + 5)
                plt.ylabel("Ellipse size [pix]", size=fontsize + 5)
                plt.title(f"Ellipse size vs azimuth", size=fontsize + 5)
                plotname = f"hartmann_ell_vs_azimuth_obsid_{sobsid}"


        else:
            meas, omeas = cpan, obsid

            # Selection of measurements smaller than maximum ellipse size (basic outlier rejection)
            selmeas = np.where(meas['ellsizesci'] <= maxsize)[0]
            measall = meas.iloc[selmeas]

            measthetasok = np.array(measall.theta_meas, dtype=float)
            measthetasmeans, measthetaslabels = cv.cluster1D(measthetasok, n_clusters=n_thetas)
            measulabels = np.unique(measthetaslabels)
            meassulabels = measulabels[np.argsort(measthetasmeans)]
            meassthetasmeans = np.sort(measthetasmeans)

            if verbose:
                plotname += f"_{sobsid}"
                print()

            for ul,uth in zip(meassulabels, meassthetasmeans):
                selul = np.where(measthetaslabels==ul)
                outputstring += f"{sobsid} {site:5s}  {label=:20s} | {ul=:2d} elevation {uth:6.2f}, {len(selul[0]):3d} meas, avg +- std : {np.nanmean(measall['ellsizesci'].iloc[selul]):7.3f} +- {np.nanstd(measall['ellsizesci'].iloc[selul]):7.3f} [pixels]\n"

                isort = np.argsort(np.array(measall.phi_meas.iloc[selul]))
                tmp = np.array(measall.ellsizesci.iloc[selul])
                meassize = tmp[isort]
                measphi = np.sort(np.array(measall.phi_meas.iloc[selul]))

                # Tilt fit
                plotfit = False
                try:
                    tau = get_tau(uth, setup=setup)
                    # This radius doesn't take the gap between CCDs into account.
                    radiusmm = np.nanmean(uth) * 3600 / 15 * 0.018

                    # fitx, fity_in = measall.phi_meas.iloc[selul], measall.ellsize.iloc[selul]
                    fitx, fity_in = measphi, meassize
                    guesssize = np.nanmean(fity_in)
                    rxhm, ryhm, normalhm, tilthm, pmaxhm, gammhm, parsm = rxry_to_flat(fitx, fity_in,
                                                                                       guesspars=[0.5, 0.5, guesssize],
                                                                                       radiusmm=radiusmm,
                                                                                       mmperpix=tau / 1000.,
                                                                                       verbose=False)
                    if pmaxhm > np.pi: pmaxhm = pmaxhm - (2 * np.pi)
                    outputstring += " " * 12 + f"Tilt:  {tilthm:7.3f} arcmin. To make it flat --> [Rx, Ry] : [{rxhm:7.3f},{ryhm:7.3f}]  phi_of_max {np.rad2deg(pmaxhm):7.2f} deg\n"
                    plotfit = True

                except:

                    outputstring += "Sine fit to cancel the tilt: did not converge\n"

                # Plot
                if verbose:

                    # plt.plot(measall.phi_meas.iloc[selul], measall.ellsize.iloc[selul], c=colors[c%len(colors)], marker='o', ls='-',
                    #          label=label + f" {uth:3.0f}")
                    plt.plot(measphi, meassize, c=colors[c%len(colors)], marker='o', ls='-',label=label + f" {uth:3.0f}")

                    if plotfit:
                        fity_out = cosine_funcfixf(fitx, *parsm)
                        plt.plot(fitx, fity_out, c=colors[c % len(colors)], alpha=0.25, marker='', ls='--')

                    plt.legend()

            # Matching measurements one by one before quantified comparison
            # --> exclude bad measures, possibly not at the same location between the reference obsid and this one
            # We first identify the closest FoV location in this obsid for each of those in the reference obsid
            # We then check that the closest match is near enough the reference measurement to be accepted as a match

            measangles = np.vstack([measall.theta_meas, measall.phi_meas]).T
            selrefok, selmeasok = [], []
            for r in selref:
                # index of the closest match in 'measall' for each valid measure in 'ref'
                idx = cv.closestPoint([[ref.theta_meas[r], ref.phi_meas[r]]], measangles)

                # Disregard the false matches, i.e. the two FoV positions differ by more than max_dtheta or max_dphi
                if (np.abs(ref.theta_meas.iloc[r] - measall.theta_meas.iloc[idx]) < max_dtheta) and (
                        np.abs(ref.phi_meas.iloc[r] - measall.phi_meas.iloc[idx]) < max_dphi):
                    selrefok.append(r)
                    selmeasok.append(idx)
                    print(
                        f"INFO: Best match: {r=}, {idx=}, [{ref.theta_meas.iloc[r]:7.3f}, {measall.theta_meas.iloc[idx]:7.3f}], [{ref.phi_meas.iloc[r]:7.3f}, {measall.phi_meas.iloc[idx]:7.3f}]  {ref['ellsizesci'].iloc[r]:6.2f} {measall['ellsizesci'].iloc[idx]:6.2f} {(ref['ellsizesci'].iloc[r] - measall['ellsizesci'].iloc[idx]):6.2f} [pixels]")
                else:
                    print(
                        f"INFO: Best match >< match: {r=}, {idx=}, [{ref.theta_meas.iloc[r]:7.3f}, {measall.theta_meas.iloc[idx]:7.3f}], [{ref.phi_meas.iloc[r]:7.3f}, {measall.phi_meas.iloc[idx]:7.3f}]  {ref['ellsizesci'].iloc[r]:6.2f} {measall['ellsizesci'].iloc[idx]:6.2f}")
                    outputstring += f'INFO: Best match >< match: {r=}, {idx=}, [{ref.theta_meas.iloc[r]:7.3f}, {measall.theta_meas.iloc[idx]:7.3f}], [{ref.phi_meas.iloc[r]:7.3f}, {measall.phi_meas.iloc[idx]:7.3f}]  {ref["ellsizesci"].iloc[r]:6.2f} {measall["ellsizesci"].iloc[idx]:6.2f}\n'

            # Select the subset of matching measures in 'ref' and 'meas'
            refok = ref.iloc[selrefok]
            measok = measall.iloc[selmeasok]

            # Identify the clusters in theta, label the data, sort the result in growing theta
            refokthetasok = np.array(refok.theta_meas, dtype=float)
            refokthetasmeans, refokthetaslabels = cv.cluster1D(refokthetasok, n_clusters=n_thetas)
            refokulabels = np.unique(refokthetaslabels)
            refoksulabels = refokulabels[np.argsort(refokthetasmeans)]
            refoksthetasmeans = np.sort(refokthetasmeans)

            measokthetasok = np.array(measok.theta_meas, dtype=float)
            measokthetasmeans, measokthetaslabels = cv.cluster1D(measokthetasok, n_clusters=n_thetas)
            measokulabels = np.unique(measokthetaslabels)
            measoksulabels = measokulabels[np.argsort(measokthetasmeans)]
            measoksthetasmeans = np.sort(measokthetasmeans)

            ### Verify overall agreement, incl. all measurements (based on avg tau)
            #tau = get_tau(np.mean(refokthetasok), setup=setup)
            taus = get_tau(refokthetasok, setup=setup)
            compare = (np.array(measok['ellsizesci']) - np.array(refok['ellsizesci'])) * taus
            if (meas_error is None) or (meas_error < 0.):
                overall_meas_error = np.nanstd(compare)
            else:
                overall_meas_error = meas_error

            # print(f"{sobsid} Overall {refok['ellsizesci']=}")
            # print(f"{sobsid} Overall {measok['ellsizesci']=}")
            # print(f"{sobsid} Overall {compare.__class__=} {compare=} {compare.shape=}")

            # max_offset = dSigma_max in the formulae
            overall_tolerance_global = (max_offset + n_sigma * np.sqrt(2.) * overall_meas_error / np.sqrt(len(compare)))
            overall_criterion_global = np.abs(np.nanmean(compare)) < overall_tolerance_global
            overall_match_global = hashok[overall_criterion_global]

            overall_tolerance_local = (max_offset + n_sigma * np.sqrt(2.) * overall_meas_error)
            overall_criterion_local = np.max(np.abs(compare)) < overall_tolerance_local
            overall_match_local = hashok[overall_criterion_local]

            outputstring += f"{sobsid} {site:5s} {label=:20s} elevations: All  {tau=:5.1f} n_meas:{len(compare):2d} {omeas} - {oref} : {np.nanmean(compare):7.3f} +- {np.nanstd(compare):7.3f}  [microns]\n"
            outputstring += " "*12 + f"Overall Match Global {np.abs(np.nanmean(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {overall_meas_error:5.2f} / sqrt({len(compare)}) = {overall_tolerance_global:6.2f} : {overall_match_global}\n"
            outputstring += " "*12 + f"Overall Match Local  {np.max(np.abs(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {overall_meas_error:5.2f} = {overall_tolerance_local:6.2f}            : {overall_match_local}\n"
            ###


            for rul, mul, ruth, muth in zip(refoksulabels, measoksulabels, refoksthetasmeans, measoksthetasmeans):
                refokselul = np.where(refokthetaslabels==rul)
                measokselul = np.where(measokthetaslabels==mul)

                print(f"ref,meas: Labels {rul}, {mul}  Thetas {ruth:.3f}, {muth:.3f}  Nb points {len(refokselul[0])}, {len(measokselul[0])}")

                # quantitative comparison
                tau = get_tau(ruth, setup=setup)
                compare = (np.array(measok['ellsizesci'].iloc[measokselul[0]]) - np.array(refok['ellsizesci'].iloc[refokselul[0]])) * tau

                print(f"ref : sel & array {len(refokselul[0])}, {len(refok['ellsizesci'].iloc[refokselul[0]])}, meas sel & array {len(measokselul[0])},  {len(measok['ellsizesci'].iloc[measokselul[0]])}, compare {len(compare)}, tau {tau}")

                #print(f"{sobsid} elevation {ruth:6.2f} {compare=}")
                if (meas_error < 0.) or (meas_error is None):
                    theta_meas_error = np.nanstd(compare)
                else:
                    theta_meas_error = meas_error

                outputstring += f"{sobsid} {site:5s} {label=:20s} elevation {ruth:6.2f} {tau=:5.1f} n_meas:{len(compare):2d} {omeas} - {oref} : {np.nanmean(compare):7.3f} +- {np.nanstd(compare):7.3f}  [microns]\n"

                # max_offset = dSigma_max in the formulae

                tolerance_global = (max_offset + n_sigma * np.sqrt(2.) * theta_meas_error / np.sqrt(len(compare)))
                criterion_global = np.abs(np.nanmean(compare)) < tolerance_global
                match_global = hashok[criterion_global]

                tolerance_local = (max_offset + n_sigma * np.sqrt(2.) * theta_meas_error)
                criterion_local = np.max(np.abs(compare)) < tolerance_local
                match_local = hashok[criterion_local]

                outputstring += " "*12 + f"Match Global {np.abs(np.nanmean(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {theta_meas_error:5.2f} / sqrt({len(compare)}) = {tolerance_global:6.2f} : {match_global}\n"
                outputstring += " "*12 + f"Match Local  {np.max(np.abs(compare)):6.2f} < {max_offset:3.1f} + {n_sigma:3.1f} * sqrt(2) * {theta_meas_error:5.2f} = {tolerance_local:6.2f}            : {match_local}\n"

                # --- CHECK MATCH ---
                # Display point-to-point match, sorted by boresight angle --- essentially for debugging purposes
                print("Match : sanity check")
                for ir, im in zip(refokselul[0], measokselul[0]):
                    print(f"Match : r_idx={ir:2d} m_idx={im:2d}  thetas: [{refok.theta_meas.iloc[ir]:6.3f}, {measok.theta_meas.iloc[im]:6.3f}]  phis: [{refok.phi_meas.iloc[ir]:8.3f}, {measok.phi_meas.iloc[im]:8.3f}]  size: {refok['ellsizesci'].iloc[ir]:6.2f} - {measok['ellsizesci'].iloc[im]:6.2f} = {refok['ellsizesci'].iloc[ir] - measok['ellsizesci'].iloc[im]:6.2f} pix = {(refok['ellsizesci'].iloc[ir] - measok['ellsizesci'].iloc[im])*tau:6.2f} um")

                """
                # Check that things are still "matchable"
                print("Match : sanity check 2")
                measanglesok = np.vstack([measok.theta_meas, measok.phi_meas]).T
                selrefok1, selmeasok1 = [], []
                #print(f"{refokselul[0]=}")
                for r in refokselul[0]:
                    # index of the closest match in 'measall' for each valid measure in 'ref'
                    #print(f"{r=} {refok.theta_meas[r]=} {refok.phi_meas[r]=}")
                    idx = cv.closestPoint([[refok["theta_meas"].iloc[r], refok["phi_meas"].iloc[r]]], measanglesok)

                    # Disregard the false matches, i.e. the two FoV positions differ by more than max_dtheta or max_dphi
                    if (np.abs(refok.theta_meas.iloc[r] - measok.theta_meas.iloc[idx]) < max_dtheta) and (
                            np.abs(refok.phi_meas.iloc[r] - measok.phi_meas.iloc[idx]) < max_dphi):
                        selrefok1.append(r)
                        selmeasok1.append(idx)
                        print(
                            f"INFO: Best match: {r=}, {idx=}, [{refok.theta_meas.iloc[r]:7.3f}, {measok.theta_meas.iloc[idx]:7.3f}], [{refok.phi_meas.iloc[r]:7.3f}, {measok.phi_meas.iloc[idx]:7.3f}]  {refok['ellsizesci'].iloc[r]:6.2f} {measok['ellsizesci'].iloc[idx]:6.2f} {(refok['ellsizesci'].iloc[r]-measok['ellsizesci'].iloc[idx]):6.2f} [pixels] {(refok['ellsizesci'].iloc[r]-measok['ellsizesci'].iloc[idx])*tau:6.2f} [microns]")
                    else:
                        print(
                            f"INFO: Best match >< match: {r=}, {idx=}, [{refok.theta_meas.iloc[r]:7.3f}, {measok.theta_meas.iloc[idx]:7.3f}], [{refok.phi_meas.iloc[r]:7.3f}, {meas.phi_meas.iloc[idx]:7.3f}]  {refok['ellsizesci'].iloc[r]:6.2f} {measok['ellsizesci'].iloc[idx]:6.2f}")
                        outputstring += f'INFO: Best match >< match: {r=}, {idx=}, [{refok.theta_meas.iloc[r]:7.3f}, {measok.theta_meas.iloc[idx]:7.3f}], [{refok.phi_meas.iloc[r]:7.3f}, {measok.phi_meas.iloc[idx]:7.3f}]  {refok["ellsizesci"].iloc[r]:6.2f} {measok["ellsizesci"].iloc[idx]:6.2f}\n'
                """
                # outputstring below = perfect match with the above --> superfluous
                # # Select the subset of matching measures in 'ref' and 'meas'
                # refok1 = refok.iloc[selrefok1]
                # measok1 = measok.iloc[selmeasok1]
                #
                # compare = (measok1['ellsizesci'] - refok1['ellsizesci']) * tau
                #
                # outputstring += f"{sobsid} {site:5s} {label=:20s} elevation {ruth:6.2f} {tau=:5.1f} n_meas:{len(compare):2d} {omeas} - {oref} : {np.nanmean(compare):7.3f} +- {np.nanstd(compare):7.3f}  [microns]\n"

    if verbose:
        print(outputstring, flush=True)

    return plotname+".png", outputstring
