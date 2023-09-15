# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:21:24 2016

@author: pierre
"""

# Python modules from the PlatoSim distribution : ~/opt/anaconda3/envs/platosim/python

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from sklearn.cluster import KMeans

def cl(obj):
    """
    cl(obj) returns the class of the input object
    """
    return (obj.__class__)

def methods(obj,verbose=False):
    """
    returns the list of existing methods on the input object
    """
    meths = [method for method in dir(obj) if not method.startswith("_")]
    if verbose:
        for m in meths: print (m)
    return meths

def stats(array):
    """
    stats(array) : returns basic statistics on the input array
    """
    import numpy as np
    print ("Shape         :", array.shape)
    array = np.ravel(array)
    array = array[np.isfinite(array)]
    print ("MIN    {0:10.3e}    MAX    {1:10.3e}".format(np.min(array), np.max(array)))
    print ("MEAN   {0:10.3e}    STDDEV {1:10.3e}".format(np.mean(array), np.std(array)))
    print ( "MEDIAN {0:10.3e}    MAD    {1:10.3e}".format(np.median(array), np.median(np.abs(np.ravel(array)-np.median(array)))))
    print ("{0:s}       MeanAD {1:10.3e}".format(" "*14, np.sum(np.abs(np.ravel(array)-np.median(array))) / float(len(np.ravel(array)))))
    return


def robustf(data,func,sigma=None,excl=None,**kwargs):
    """
    Will exclude some data from the input array before computing the function 'func'
    Either sigma or excl must be provided
    sigma : sigma-clipping the array
    excl  : the 'excl' lowest and highest values are excluded
    """
    data = data[np.isfinite(data)]
    if sigma is not None:
        m = np.mean(data)
        data = data[np.where(np.abs(data-m) <= sigma * np.std(data))]
    elif excl is not None:
        data = np.sort(data)[excl:-excl]
    else:
        print(f"Please provide either 'sigma' or 'excl'")
        return
    return func(data,**kwargs)


def reimport(func, verbose=True):
    """
    Update the definition of the input function by reloading it

    Import and reload the module of a function
    Re-import the function
    """
    from importlib import reload, import_module
    import sys

    fmodule = func.__module__
    if verbose:
        print(f"import_module({fmodule})")
    import_module(fmodule)

    fmodule = sys.modules[func.__module__]
    if verbose:
        print(f"reload({fmodule})")
    reload(fmodule)

    fmodule = func.__module__
    if verbose:
        print(f"import_module({fmodule})")
    import_module(fmodule)

    print('ok')

    return

# Print list items one by one
def print1(items):
    for i,item in enumerate(items):
        print(f"{i:5d} {item}")

# Print a matrix with consistent format for all values
def printm(matrix,rounding=4):
    if rounding is None:
        print(matrix)
    else:
        print(f"{np.round(matrix,rounding)}")

# Print dictionary content, one [key,value] / line
def printh(inputDict,prefix=""):
    """printh(inputDict,prefix="")
    Prints all key,value pairs in the input dictionary
    The indentation reflects the dictionary structure
    """
    for k,v in zip(inputDict.keys(),inputDict.values()):
        baseprefix=prefix
        if isinstance(v,dict):
            baseprefix+=" "*4
            printh(v,prefix=baseprefix)
        else:
            print (f"{baseprefix}{k} | {v}")

# Sine & Cosine func - basic
def sine_func(x, freq, amplitude, phase, offset):
    return np.sin(x * freq + phase) * amplitude + offset
def cosine_func(x, freq, amplitude, phase, offset):
    return np.cos(x * freq + phase) * amplitude + offset

# Sine & Cosine func - period fixed to 360 degrees
def sine_funcfixf(x, amplitude, phase, offset):
    return np.sin(x * 2. * np.pi / 360. + phase) * amplitude + offset
def cosine_funcfixf(x, amplitude, phase, offset):
    return np.cos(x * 2. * np.pi / 360. + phase) * amplitude + offset

# Fitting
def mypolyfit(x,y,order=1, verbose=1):
    """
    coeff, yfit = mypolyfit(x,y,order=1, verbose=1)
    """
    from numpy.lib.polynomial import polyfit, poly1d
    coeffs = polyfit(x,y,order)
    polyModel = poly1d(coeffs)
    if verbose: print ("Fit coeffs:", coeffs)
    return coeffs,polyModel(x),polyModel

def gaussModel(x, a, b, c):
    return a * np.exp(-(x - b)**2.0 / (2 * c**2))

def mygaussfit(x,y,verbose=1):
    from scipy import optimize
    popt, pcov = optimize.curve_fit(gaussModel, x, y)
    yfit = gaussModel(x, *popt)
    return popt, yfit

def fitCircle(cont,verbose=False):
    """
    input 'cont' = array of shape [n,2] containing the [x,y] coordinates of the points to be fit

    output = params, ellipse
        params = [x_center, y_center, radius]
        circle is an Circle object
    """
    from matplotlib.patches import Circle
    from skimage.measure import CircleModel

    circ = CircleModel()
    success = circ.estimate(cont)

    if verbose:
        print(f"Successful scikit Circle fit {success}")

    xc, yc, radius = circ.params
    circle_patch = Circle((yc, xc), radius=radius, color="y", fill=False, lw=2, ls='--', alpha=0.5)#, edgecolor='yellow', facecolor='none')

    return circ.params, circle_patch


def fitEllipseScikit(cont,verbose=False):
    """
    input 'cont' = array of shape [n,2] containing the [x,y] coordinates of the points to be fit

    output = params, ellipse
        params = [x_center, y_center, a, b, angle]
        ellipse is an Ellipse object
    """
    from matplotlib.patches import Ellipse
    from skimage.measure import EllipseModel

    ell = EllipseModel()
    success = ell.estimate(cont)

    if verbose:
        print(f"Successful scikit ellipse fit {success}")

    xc, yc, a, b, theta = ell.params
    ell_patch = Ellipse((yc, xc), width=2. * a, height=2. * b, angle=np.rad2deg(theta), color="y", fill=False, lw=2, ls='--', alpha=0.5)#, edgecolor='yellow', facecolor='none')

    # pass angle to degrees
    params = ell.params
    params[-1] = np.rad2deg(params[-1])

    return params, ell_patch

def fitEllipse(cont):
    """
    input 'cont' = array of shape [n,2] containing the [x,y] coordinates of the points to be fit

    output = params, ellipse
        params = [x_center, y_center, a, b, angle]
        ellipse is an Ellipse object
    """
    import numpy
    from matplotlib.patches import Ellipse

    x = cont[:, 0]
    y = cont[:, 1]

    x = x[:, None]
    y = y[:, None]

    D = numpy.hstack([x * x, x * y, y * y, x, y, numpy.ones(x.shape)])
    S = numpy.dot(D.T, D)
    C = numpy.zeros([6, 6])
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    E, V = numpy.linalg.eig(numpy.dot(numpy.linalg.inv(S), C))

    # Method 1 was erronneous and corrected here
    # See https://stackoverflow.com/questions/39693869/fitting-an-ellipse-to-a-set-of-data-points-in-python
    # if method==1:
    #    n=numpy.argmax(numpy.abs(E))
    # else:
    n = numpy.argmax(E)
    a = V[:, n]

    # -------------------Fit ellipse-------------------
    b, c, d, f, g, a = a[1] / 2., a[2], a[3] / 2., a[4] / 2., a[5], a[0]
    num = b * b - a * c
    cx = (c * d - b * f) / num
    cy = (a * f - b * d) / num

    angle = 0.5 * numpy.arctan(2 * b / (a - c)) * 180 / numpy.pi
    up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
    down1 = (b * b - a * c) * ((c - a) * numpy.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    down2 = (b * b - a * c) * ((a - c) * numpy.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    a = numpy.sqrt(abs(up / down1))
    b = numpy.sqrt(abs(up / down2))

    # ---------------------Get path---------------------
    ell = Ellipse((cy, cx), width=a * 2., height=b * 2., angle=angle, color="r", fill=False, lw=2,
                                              ls=':', alpha=0.5)
    # ell_coord=ell.get_verts()

    params = np.array([cx, cy, a, b, angle])

    return params, ell


def ccd_positions(ccd_corners, verbose=True):
    """
    INPUT
    ccd_corners = focal plane coordinates (mm) of the ccd corner pixels
                  These pixels are assumed to be ordered according to
                  the EM FPA EIDP : BL, TL, TR, BR (wrt the CCD ref. frame as defined in the commanding manual)

    verbose : prints info when true

    Example input, (EM FPA), from
    PTO-E2V-FPA-DP-00000001v2_PLATO\ FPA\ EM01\ EIDP_CCD_pixel_corner_coordinates.pdf  Annex M, table starting on pg 3
    # Corner Pixel FOCAL PLANE COORDINATES (mm)
    #               Bottom Left (0,0)         TL               TR                  BR
    cornerfpc= {}
    cornerfpc[4] = [[ 81.854,  0.958], [ 0.342, 0.951], [  0.336, 82.113], [ 81.498, 82.120]]
    cornerfpc[3] = [[  0.991,-81.516], [ 0.987,-0.354], [ 82.150, -0.350], [ 82.153,-81.512]]
    cornerfpc[2] = [[-81.483, -0.991], [-0.321,-0.987], [ -0.317,-82.149], [-81.479,-82.153]]
    cornerfpc[1] = [[ -0.964, 81.465], [-0.963, 0.303], [-82.125,  0.302], [-82.126, 81.464]]


    OUTPUT
    ccd_orientation : as defined in the setup
                      ccd_orientation ~ [180, 270, 0, 90]
    EM :
     origin_offset_x [-0.964, -0.991, -0.991, -0.958]
     origin_offset_y [81.465, 81.483, 81.516, 81.854]
     orientation
     1: 180.00070594341577,
     2: 270.0028237736609,
     3: 0.0026472791094462877,
     4: 90.06635297352653}

    """
    cornerfpc = ccd_corners

    origin_offset_x = [cornerfpc[1][0][0], cornerfpc[2][0][1], -cornerfpc[3][0][0], -cornerfpc[4][0][1]]
    origin_offset_y = [cornerfpc[1][0][1], -cornerfpc[2][0][0], -cornerfpc[3][0][1], cornerfpc[4][0][0]]

    hcorners = ["Y-left  ", "X-top   ", "Y-right ", "X-bottom"]
    ccdsideangles = {}
    ccdxyangles = {}
    ccdxybaselineangles = {1: 180, 2: 270, 3: 0, 4: 90}
    ccd_orientation = {}

    for ccd in [1, 2, 3, 4]:
        if verbose: print()
        angs = [0, 0, 0, 0]
        for i in range(4):
            a = cornerfpc[ccd][i]
            b = cornerfpc[ccd][(i + 1) % 4]
            ang = np.rad2deg(np.arctan((b[1] - a[1]) / (b[0] - a[0])))
            angs[i] = ang
            if verbose: print(f"{ccd=} {hcorners[i]} ang={np.round(ang, 4):9.4f}")
        ccdsideangles[ccd] = angs
        ccdxyangles[ccd] = [(angs[1] + angs[3]) / 2., (angs[0] + angs[2]) / 2.]

        # Bring "vertical" axes to positive values (for the 90 deg correction between x & y to deliver smth close to 0)
        if ccd in [2, 4]:
            ccdxyangles[ccd][0] = ccdxyangles[ccd][0] if (ccdxyangles[ccd][0] >= 0) else (ccdxyangles[ccd][0] + 180.)
        elif ccd in [1, 3]:
            ccdxyangles[ccd][1] = ccdxyangles[ccd][1] if (ccdxyangles[ccd][1] >= 0) else (ccdxyangles[ccd][1] + 180.)

        if verbose:
            print(f"{ccd=}  X-axis : {np.round(ccdxyangles[ccd][0], 4)}  Y-axis : {np.round(ccdxyangles[ccd][1], 4)}")

        ccd_orientation[ccd] = ((ccdxyangles[ccd][0] + ccdxyangles[ccd][1] - 90.) / 2. + ccdxybaselineangles[ccd])
        if verbose: print(f"{ccd=} orientation: {np.round(ccd_orientation[ccd], 4)}")

    return origin_offset_x, origin_offset_y, ccd_orientation


def is_movement_positive(current,setpoint,avoidance=3.):
    """
    gives the direction of movement (pos:True, neg:False)
    """
    import numpy as np
    if setpoint < (-180+avoidance) or setpoint > (180-avoidance):
        raise Exception

    current = current % 360

    if current > 180:
        current = current - 360.
    elif current < -180:
        current = current + 360.

    returnhash = {1.:True, -1.:False, 0.:0}
    return returnhash[np.sign(setpoint-current)]


def fileMatch(fileList, stringList):
    """
    fileMatch(fileList, stringList)

    returns the list of files from fileList in which all strings from stringList can be found, in any order
    Case sensitive
    """
    import fnmatch
    while (len(stringList) > 1):
        fileList = fileMatch(fileList, [stringList.pop()])
    return [file for file in fileList if fnmatch.fnmatch(file, '*' + stringList[0] + "*")]


def fileSelect(stringList, location="./", listOrder=0):
    """
    fileSelect(stringList, location="./", listOrder=0)

    Returns a list of all files in 'location' with name matching every string in the list
    If listOrder is True, the ordering is forced to be identical to the one in stringList
    """
    import os, fnmatch
    allfiles = os.listdir(location)
    if listOrder:
        pattern = "*"
        i = 0
        while i < len(stringList):
            pattern += stringList[i] + "*"
            i += 1
        return [file for file in allfiles if fnmatch.fnmatch(file, pattern)]
    else:
        return fileMatch(allfiles, stringList)


def closestPoint(point, points):
    """
    Find in 'points' the index of the nearest point to 'point'

    point & points are numpy arrays with shapes [1,2] and [n,2]

    Usage
    point = np.zeros([1,2])
    point[:,:] = [x,y]
    index = closestPoint(point,points)

    """
    from scipy.spatial import distance
    closest_index = distance.cdist(point, points).argmin()
    return closest_index


def allRoots(x, y, rootfunction=None):
    """
    SYNTAX
    xroots = allRoots(x,y, rootfunction=<rootfunction>)

    PURPOSE
    Find all roots (y=0) in a tabulated function (x,y)

    INPUTS
    x,y : input function
    rootfunction : any root-finding function from scipy.optimize.zeros (default = ridder)

    OUTPUT
    The x-values of the roots
    """
    import numpy as np
    from scipy.interpolate import interp1d
    from scipy.optimize.zeros import ridder

    if rootfunction is None:
        rootfunction = ridder

    #
    # Build an interpolator over the input data
    f = interp1d(x, y, kind='linear')
    #
    # Select segments where the sign is changing
    idx = np.where((y * np.roll(y, 1))[1:] <= 0.)[0]
    #
    # Compute the position of the root in every segment
    # The unique function is applied to be robust vs segments at y=0.
    return np.unique(np.array([rootfunction(f, x[i], x[i + 1]) for i in idx]))


def ambient_focus(boresight_angle):
    """
    Returns the focus location at ambient wrt L6, for a given 'boresight_angle' from the optical axis

    Input calibration curve : Email L. Clermont 14-09-2021
    """
    from scipy.interpolate import interp1d
    input_curve = np.array([[0,    5.42559],
    [1,     5.42391],
    [2,     5.41888],
    [3,     5.4106],
    [4,     5.39918],
    [5,     5.38481],
    [6,     5.3677],
    [7,     5.34809],
    [8,     5.32625],
    [9,     5.30241],
    [10,    5.27679],
    [11,    5.2495],
    [12,    5.22049],
    [13,    5.18947],
    [14,    5.15574],
    [15,    5.11804],
    [16,    5.07425],
    [17,    5.02104],
    [18,    4.95335],
    [19,    4.86365]])

    f = interp1d(input_curve[:,0],input_curve[:,1], kind='linear')

    return f(boresight_angle)

def imshow(image,figname=None,figsize=None,xlim=None,ylim=None,vsigma=1,**kwargs):
    """
    Short version of plt.imshow including presets in the vscale
    """

    if xlim is None:
        xmin,xmax = [0,image.shape[0]]
    else:
        xmin,xmax = xlim[0],xlim[1]
    if ylim is None:
        ymin,ymax = [0,image.shape[1]]
    else:
        ymin,ymax = ylim[0],ylim[1]

    sel = np.where(image[ymin:ymax,xmin:xmax] !=0 )
    imean, istd = np.mean(image[ymin:ymax,xmin:xmax][sel]), np.std(image[ymin:ymax,xmin:xmax][sel])
    vmin, vmax = imean - vsigma * istd, imean + vsigma * istd

    kwargs.setdefault('origin','lower')
    kwargs.setdefault('interpolation','nearest')
    kwargs.setdefault('vmin',vmin)
    kwargs.setdefault('vmax',vmax)
    #kwargs.setdefault('cmap',cm.inferno)

    plt.figure(figname,figsize=figsize)
    #plt.imshow(image, vmin=vmin, vmax=vmax, **kwargs)
    plt.imshow(image, **kwargs)

    return


def showLayer(cube_number, layer_number, filenames, vsigma=2, obsid=None, full=False, **kwargs):
    """
    Selects 'cube_number'-th cube from the list of 'filenames' (absolute paths)
    Displays the 'layer_number'-th layer of that cube

    vsigma = plotting option (automatic z-scale)
    obsid  = for plot decoration
    """
    #import time
    from astropy.io import fits
    from matplotlib import cm

    print()
    print("DEPRECATION WARNING:")
    print("    . To show a layer in a cube: camtest.analysis.image_utils.show_layer")
    print("    . To show an entire CCD, eventually including pre- and over-scans, use camtest.analysis.image_utils.show_ccd")
    print()

    filename = filenames[cube_number]
    hduc = fits.open(filename)

    extnames = np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))],dtype=object)
    icube = np.where([i.find("IMAGE")>=0 for i in extnames])[0][0]+1

    layer = np.array(hduc[icube].data[layer_number, :, :], dtype=float)
    sccd = f"CCD_{hduc[2].header['CCD_ID']}{hduc[2].header['SENSOR_SEL']}"
    drow,dcol = layer.shape

    kwargs.setdefault('cmap',cm.inferno)

    if not full:
        imshow(layer, vsigma=vsigma, **kwargs)
    else:
        try:
            ispre = np.where([i.find("SPRE") >= 0 for i in extnames])[0][0]+1
            spre = np.array(hduc[ispre].data[layer_number,:,:], dtype=float)
            drowspre, dcolspre = spre.shape
        except:
            print("No Serial Prescan Found")
            drowspre, dcolspre, spre = 0, 0, None
        try:
            isover = np.where([i.find("SOVER") >= 0 for i in extnames])[0][0]+1
            sover = np.array(hduc[isover].data[layer_number,:,:], dtype=float)
            drowsover, dcolsover = sover.shape
        except:
            print("No Serial Overscan Found")
            drowsover, dcolsover, sover = 0, 0, None
        try:
            ipover = np.where([i.find("POVER") >= 0 for i in extnames])[0][0]+1
            pover = np.array(hduc[ipover].data[layer_number,:,:], dtype=float)
            drowpover, dcolpover = pover.shape
        except:
            print("No Parallel Overscan Found")
            drowpover, dcolpover, pover = 0, 0, None

        image = np.zeros([drow+drowpover,dcol+dcolspre+dcolsover])
        image[0:drow+drowpover, dcolspre:dcolspre+dcol] = layer
        if spre is not None:
            image[0:drow+drowpover, 0:dcolspre] = spre
        if sover is not None:
            image[0:drow+drowpover, dcolspre+dcol:dcolspre+dcol+dcolsover] = sover
        if pover is not None:
            image[drow:drow+drowpover, dcolspre:dcolspre+dcol] = pover

        imshow(image, vsigma=vsigma, **kwargs)

    plt.colorbar()
    plt.title(f"{obsid=} cube={cube_number} layer={layer_number} {sccd}", size=20)



def csvLoad(stringList, location="./", listOrder=0, verbose=True, **kwargs):
    """
    Parameters
    ----------
    stringList : TYPE
        DESCRIPTION.
    location : TYPE, optional
        DESCRIPTION. The default is "./".
    listOrder : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    loaded np array
    """
    stringList.append("csv")

    files = fileSelect(stringList=stringList, location=location, listOrder=listOrder)
    # print(files)
    if len(files) > 1:
        if verbose:
            print("WARNING: Multiple files found")
            print("         please refine your selection via a more restrictive stringList")
            print(f"{files}")
        return None
    elif len(files) < 1:
        if verbose:
            print("WARNING: NO file found")
            print("         please review your selection (stringList)")
        return None
    else:
        kwargs.setdefault("delimiter", ",")
        result = ascii.read(location + files[0], **kwargs)
        return result


def get_frame_times(filenames, ccd_number=None, ccd_side=None):
    """
    Extract the absolute times from all frames in the input data files
    Concatenated into a 1d array
    """
    from astropy.io import fits
    from egse.system import time_since_epoch_1958

    result = []

    for filename in filenames:
        hduc = fits.open(filename,mode='readonly')

        extnames = np.array([hduc[i].header["EXTNAME"] for i in range(1, len(hduc))], dtype=object)

        if ccd_number is None and ccd_side is None:
            iwcs = np.where([i.find("WCS-TAB") >= 0 for i in extnames])[0][0] + 1
            iimage = np.where([i.find("IMAGE") >= 0 for i in extnames])[0][0] + 1
        elif ccd_number and ccd_side:
            iwcs = np.where([i.find(f"WCS-TAB_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0] + 1
            iimage = np.where([i.find(f"IMAGE_{ccd_number}_{ccd_side}") >= 0 for i in extnames])[0][0] + 1
        else:
            print(f"CRITICAL: {ccd_number=} and {ccd_side=} must be either None, or specified together")

        start_time = time_since_epoch_1958(hduc[iimage].header["DATE-OBS"])

        rel_time = np.array(hduc[iwcs].data,dtype=float)

        result.append(rel_time+start_time)

    return np.ravel(np.array(result))


def cluster1D(data, n_clusters=6):
    """
    cluster1D(data, n_clusters=6)

    K-means clustering of a 1D array

    Input
    data: 1D array
    n_clusters

    Output
    labels: 1D array of the cluster number of each datapoint (same shape as data, values in [0,n_clusters-1]
    """
    km = KMeans(n_clusters=n_clusters)
    x = np.reshape(data, (-1,1))
    km.fit(x)
    labels = km.predict(x)
    return km.cluster_centers_.flatten(), labels.flatten()


def rescale(data, dmin, dmax):
    """
    rescale the input 'data' to the input boundaries [dmin, dmax]
    """
    imin,imax = np.min(data), np.max(data)
    return (data - imin) / (imax - imin) * (dmax - dmin) + dmin

def get_color(c):
    """
    Input
    c: int

    Get next color from a predefined list of colors, cycling through the list again if c > len(predefined-list)
    """
    orange = (1., 0.75, 0.)
    gray = (0.5, 0.5, 0.5)
    purple = (1, 0, 1)
    pink = (1., 0.5, 0.75)
    lightgray = (0.75, 0.75, 0.75)
    lightgreen = (0.5, 1, 0.5)
    lightblue = (0.5, 0.5, 1.0)
    lightorange = (1., 0.9, 0.5)
    # lightpink = (1., 0.75, 0.9)
    # darkorange = (0.8, 0.55, 0)
    # verylightblue = (0.75, 0.75, 1.0)
    # verylightgreen = (0.75, 1.0, 0.75)
    # verylightgray = (0.9, 0.9, 0.9)
    # brown = (0.7, 0.6, 0.2)
    # darkgray = (0.25, 0.25, 0.25)

    colors = ['k', lightgreen, 'g', 'c', 'r', orange, 'b', lightblue, 'm', purple, pink, gray, lightgray, lightorange]

    return colors[c%len(colors)]

def colors_gen(n, verbose=False):
    """
    Generate n colors in a 'rainbow' sequence
    """
    colors = []
    for i in range(n):
        r = (1+np.cos(2*np.pi * (i/n))) / 2.
        g = (1+np.cos(2*np.pi * (i/n + 1/3.))) / 2.
        b = (1+np.cos(2*np.pi * (i/n + 2/3.))) / 2.
        colors.append((r,g,b))
        if verbose:
            print(f"{i}, ({r:5.2f},{g:5.2f},{b:5.2f})")
    return colors

def grays_gen(n, darkest=0., lightest=0.9):
    """
    Generates gray-scale colors, with the darkest and lightest fixed by the corresponding parameters
        darkest : default = 0.0   (black = 0.0)
        lightest: default = 0.9   (white = 1.0)
    """
    return [(g,g,g) for g in np.linspace(darkest,lightest,n)]


def mylombscargle(x, y, oversampling=5, normalise=True, verbose=True):
    """
    mylombscargle(x, y, oversampling=5)

    x,y : input signal
    oversampling : defines the sampling, i.e. the frequencies sampled in 1/Dx, n/Dx
                   where n = nb of data points and Dx = max(x)-min(x)
    normalize : the periodogram is normalised to its peak frequency

    OUTPUT:
    frequencies, in rad/s
    periodogram
    """
    import scipy.signal
    n = len(x)
    x_span = np.ptp(x)
    freqs = np.linspace(1/x_span, n/x_span, oversampling * n)
    periodogram = signal.lombscargle(x, y, freqs)

    if verbose:
        print(f"Peak frequency: {freqs[periodogram.argmax()]:8.3f}")

    return freqs, periodogram

def kde_modes(data1d, bw_method=0.1, kde_threshold=None, verbose=True):
    """
    data1d : np.array 1D

    bw_method : driving the sensitivity of the KDE. Must be either 'scott', 'silverman' or a scalar
                default = 0.1

    kde_threshold = significance level to recognise a non-zero region of the KDE as a mode in the distribution
                    Default (None) : the weight of 2 data samples
    """
    from scipy.stats import gaussian_kde

    kde = gaussian_kde(data1d,bw_method=bw_method)
    xkde = np.arange(np.min(data1d)-0.1,np.max(data1d)+0.1,1.e-3)
    ykde = kde.pdf(xkde)

    # Default KDE threshold = weight of 2 samples
    if kde_threshold is None:
        kde_threshold = 2./len(data1d)

    ykde_th = ykde - kde_threshold

    # Locate the modes in the multimodal distribution
    sel = np.where(ykde_th > 0.)[0]
    modes, nmodes = [], 0
    modes.append([sel[0]])
    for i in sel[1:]:
        if i-1 in sel:
            modes[nmodes].append(i)
        else:
            nmodes += 1
            modes.append([i])

    data_modes = []
    for mode in modes:
        sel = np.where((data1d >= xkde[mode[0]]) & (data1d <= xkde[mode[-1]]))[0]
        data_modes.append(sel)

    if verbose:
        plt.figure()
        plt.hist(data1d, bins=50)
        plt.plot(xkde, ykde, 'k.-')
        for mode in modes:
            plt.plot(xkde[mode], ykde[mode], 'r.-')

    return data_modes

