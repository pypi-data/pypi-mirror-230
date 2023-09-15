"""
Collection of functions to compute different geometries of test-positions throughout the FoV.

Circular geometries : the test-positions are distributed over circles around the optical axis

Rectangular : the test-positions are distributed over a regular grid (raster)

Equi-surface : the test-positions are distributed over a collection of cells that all have the same area
               the cells are distributed over a number of circles, i.e. cells = [1,2,3,...] means
                . one central cell/ quadrant
                . two cells/quadrant on a second annulus
                . three cells/quadrant on the third
                ...

"""
import textwrap

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from egse.coordinates import focal_plane_to_ccd_coordinates, focal_plane_coordinates_to_angles, \
    undistorted_to_distorted_focal_plane_coordinates, angles_to_focal_plane_coordinates, ccd_to_focal_plane_coordinates,\
    distorted_to_undistorted_focal_plane_coordinates

from egse.settings import Settings
from egse.state import GlobalState
from egse.exceptions import Abort


# Gap between CCDs in mm
# a = 2.4
# Radius of the FoV in degrees
# radiusdeg = 18.87
# Radius of the FoV in mm
# R = radiusmm = radiusdeg * 3600 / pixelsizesec * pixelsizemm  # 81.5184


def deg2mm(angleFromOA):
    """
    Assumes the PLATO platescale and pixel size and transforms an angular distance
    from the optical axis into mm from the optical axis
    """

    # conversion degreeFromOA to mmFromOA
    # degreeToMm = 3600. / plateScale * pixelSize = 4.32

    plateScale = 15  # arcsec / pixel
    pixelSize = 0.018  # mm

    pixelFromOA = angleFromOA * 3600 / plateScale

    mmFromOA = pixelFromOA * pixelSize

    return mmFromOA


#######################################
## CIRCULAR DISTRIBUTION (4 quadrants)
#######################################


def circleFieldAngles(n,radius,offset=0.5, cam='n',verbose=False):
    """
    INPUT
    n : nb of fov points to visit on the circle
    radius : boresight angle of all the fov positions to define
    offset : offset in azimuth wrt starting at azimuth 0.
             The offset is specified in units of the azimuthal difference between 2 consecutive points
             The default = 0.5, keeping the points closest to the edge of the CCDs at equal distance from the gap.
    cam = 'n' or 'f' : normal of fast camera
    verbose : debug prints or not
    """

    totangle = {'n': 2 * np.pi, 'f': np.pi / 2.}

    # For F-CAM, we first compute 1 quadrant, and duplicate it later
    if cam == 'f': n = n // 4

    phis = np.array([totangle[cam] * i / n for i in range(n)])
    phis += offset * totangle[cam] / n
    phis = np.rad2deg(phis)

    thetas = np.ones_like(phis) * radius

    angles = np.stack([thetas,phis],axis=1)

    return angles


def circleCoordinates(n, radius, offset=0.5, cam='n', verbose=False):
    """
    Return the x,y coordinates of n points uniformly located on a circle or radius "radius" [deg]
    offset: initial angular shift between x-axis and first point, relative to the angular distance between 2 points

    n : number of points distributed on the circle. Must be a multiple of 4
    cam : must be in ['n','f']
          for n-cam, we work with the whole field (4 CCDs, full circles on 360 degrees)
          for f-cam, we provide just one CCD (90 degrees), cos' x > mid-ccd must be excluded (see)
    """
    totangle = {'n': 2 * np.pi, 'f': np.pi / 2.}

    # For F-CAM, we first compute 1 quadrant, and duplicate it later
    if cam == 'f': n = n // 4

    xy = np.zeros([n, 2])

    angles = np.array([totangle[cam] * i / n for i in range(n)])
    angles += offset * totangle[cam] / n

    if verbose: print("Circle Start", xy.shape)

    xy[:, 0] = radius * np.cos(angles)
    xy[:, 1] = radius * np.sin(angles)

    if cam == 'f':
        # Conversion from degrees to mm
        deg2mm = 4.32
        # F-CAM : Maximum 'x' coordinate in each quadrant (= 1/2 field = 9 degrees)
        xmax = 9. * deg2mm
        # Eliminate points in the field with x outside of the F-CAM FoV
        xx, yy = [], []
        for i, j in zip(xy[:, 0], xy[:, 1]):
            if i <= xmax:
                xx.append(i)
                yy.append(j)
        xnp, ynp = np.array(xx), np.array(yy)
        if verbose: print("Circle FCAM - Kept / quadrant", len(xx))

        del xy
        #
        # Propagate solution to all 4 quadrants
        for theta in [np.pi / 2. * (i + 1) for i in range(3)]:
            R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
            xrot, yrot = R @ [xnp, ynp]
            xx.extend(np.array(xrot)[0, :])
            yy.extend(np.array(yrot)[0, :])
        if verbose: print(len(xx), len(yy))
        xy = np.vstack([xx, yy]).T
        if verbose: print("Circle FCAM FULL", xy.shape)

    return xy


def circlesCoordinates(ns=None, radii=None, offset=0.5, verbose=False):
    """
    Return the x,y coordinates of n points uniformly located on a set of circles of radii "radii" (n/circle, radii in deg)
    offset: initial angular shift between x-axis and first point, relative to the angular distance between 2 points
    """
    import numpy as np

    if ns is None:
        ns = [4 * (i + 1) for i in range(9)]
    if radii is None:
        radii = [2 * 4.32 * (i + 1) for i in range(9)]

    ns = np.array(ns)
    nmeas = np.sum(ns)
    xy = np.zeros([0, 2])
    for n, radius in zip(ns, radii):
        circlexy = circleCoordinates(n, radius, offset, cam='n')
        if verbose: print("Shapes", n, radius, xy.shape, circlexy.shape)
        xy = np.vstack([xy, circlexy])
        if verbose: print("Shapes", n, radius, xy.shape, circlexy.shape)
        if verbose: print()
    if verbose: print(xy.shape)
    return np.reshape(xy, [nmeas, 2])


def circlesCoordinatesFCAM(ns=None, radii=None, offset=0.5, verbose=False):
    """
    Return the x,y coordinates of n points uniformly located on a set of circles of radii "radii" (n/circle, radii in deg)
    offset: initial angular shift between x-axis and first point, relative to the angular distance between 2 points
    """
    import numpy as np

    if ns is None:
        ns = [4 * (i + 1) for i in range(9)]
    if radii is None:
        radii = [2 * 4.32 * (i + 1) for i in range(9)]

    ns = np.array(ns)
    nkept = []
    xy = np.zeros([0, 2])
    for n, radius in zip(ns, radii):
        circlexy = circleCoordinates(n, radius, offset, cam='f')
        if verbose: print("Shapes", n, radius, xy.shape, circlexy.shape)
        xy = np.vstack([xy, circlexy])
        if verbose: print("Shapes", n, radius, xy.shape, circlexy.shape)
        if verbose: print()
        nkept.append(len(circlexy[:, 0]))

    nkept = np.array(nkept)
    nmeas = np.sum(nkept)

    if verbose: print(xy.shape, nkept, nmeas)
    return np.reshape(xy, [nmeas, 2]), nkept


###########################################
## GRID DISTRIBUTION  (Raster, 4 quadrants)
###########################################

def squareCoordinates(cam='f', dxy=2.5, x0=None):
    """
    Uniform, square distribution of field points --> F-CAM

    dxy in deg
    """
    # Max radius
    radiusMax = 18.
    # Max x coordinate
    xmax = {'f': 9., 'n': 18.}
    # x & y expected in mm --> scaling factor
    deg2mm = 4.32
    if x0 is None:
        x0 = dxy / 2.
    xi = x0
    x = []
    while xi < xmax[cam]:
        x.append(xi)
        xi += dxy
    yi = x0
    y = []
    while yi < radiusMax:
        y.append(yi)
        yi += dxy
    x2d, y2d = np.meshgrid(x, y)
    #
    # Scale from degrees to mm
    xall = np.ravel(x2d) * deg2mm
    yall = np.ravel(y2d) * deg2mm
    # Remove points falling out of field
    xx, yy = [], []
    for i, j in zip(xall, yall):
        if np.sqrt(i * i + j * j) <= (radiusMax * deg2mm):
            xx.append(i)
            yy.append(j)
    xnp, ynp = np.array(xx), np.array(yy)
    #
    # Rotation Matrix
    for theta in [np.pi / 2. * (i + 1) for i in range(3)]:
        #R = np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        R = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        xrot, yrot = R @ [xnp, ynp]
        xx.extend(np.array(xrot)[0, :])
        yy.extend(np.array(yrot)[0, :])
    return np.array(xx), np.array(yy)


################################################################################
### EQUI-SURFACE DISTRIBUTIONS -- IGNORING INTER-CCD GAP -- ONE QUADRANT
################################################################################


# Neglecting the central dead-cross between CCDs
def equi_surface_radii_fullquadrant(radius, cells=None):
    """
    Compute the radii of the rings making sure all cells occupy the same area
    """
    if cells is None:
        cells = [1,2,3,4]

    cells = np.array(cells)
    nslices = len(cells)
    ncells = np.sum(cells)
    radii = np.zeros(nslices)

    # Surface of each individual cell = surface of the quadrant / nb of cells
    unit_surface = (np.pi * radius * radius) / 4. / ncells

    # inner surface = surface of all rings 'inside' and including the current one=
    inner_surface = 0.

    for slice in range(nslices):
        slice_area = unit_surface * cells[slice]

        inner_surface += slice_area

        radii[slice] = np.sqrt(4. * inner_surface / np.pi)

    return radii


def equi_surface_coordinates_fullquadrant(radius, cells=None, midradius=True, verbose=False):
    """

    Parameters
    ----------
    radius : TYPE
        DESCRIPTION.
    cells : TYPE, optional
        DESCRIPTION. The default is [1,2,3,4].

    midradius : used to compute the radius of the points
        midradius = True : the point is at half the thickness of the slice
                  = False : the point is at the radius where half the surface
                           of the cell is outside, and half inside. This depends
                           on the cell geometry -- not implemented

    Returns
    -------
    x,y = np.arrays of length = number of cells

    """
    if cells is None:
        cells = [1,2,3,4]

    cells = np.array(cells)
    nslices = len(cells)

    slice_radii = equi_surface_radii_fullquadrant(radius=radius, cells=cells)

    xs, ys = [], []

    inner_radius = 0.
    for slice in range(nslices):
        if midradius:
            point_radius = (slice_radii[slice] + inner_radius) / 2.
        else:
            raise Exception("midradius - False is not implemented")

        inner_radius = slice_radii[slice]
        #
        # angular span of a cell
        cell_span = np.pi / 2. / (cells[slice])

        point_angles = np.array([(cell_span / 2. + i * cell_span) for i in range(cells[slice])])
        xs.append(point_radius * np.cos(point_angles))
        ys.append(point_radius * np.sin(point_angles))

        if verbose:
            print(f"slice {slice} radius {point_radius:.3f} angles {[np.rad2deg(i) for i in point_angles]}")

    x1d = np.array([point for aslice in xs for point in aslice])
    y1d = np.array([point for aslice in ys for point in aslice])

    return x1d, y1d


def equi_surface_edges_fullquadrant(radius, cells=None, alledges=False):
    """
    equi_surface_edges_fullquadrant(radius, cells=None, alledges=False)

    This function computes cell-edges in equi-surface distributions.
    It is only relevant for display purposes.

    alledges = False (default) : the edges at 0 & 90 degrees are not included

    """
    if cells is None:
        cells = [1,2,3,4]

    alledges = {False: 0, True: 1}[alledges]

    cells = np.array(cells)
    nslices = len(cells)

    outer_radii = equi_surface_radii_fullquadrant(radius=radius, cells=cells)

    innerxys, outerxys = [], []

    inner_radius = 0.
    for slice in range(nslices):
        outer_radius = outer_radii[slice]

        # angular span of a cell
        cell_span = np.pi / 2. / (cells[slice])

        edge_angles = np.array([(i * cell_span) for i in range(1 - alledges, cells[slice] + alledges)])

        for angle in edge_angles:
            innerxys.append([inner_radius * np.cos(angle), inner_radius * np.sin(angle)])
            outerxys.append([outer_radius * np.cos(angle), outer_radius * np.sin(angle)])

        inner_radius = outer_radius

    return np.array(innerxys), np.array(outerxys)



#####################################################################################
### EQUI-SURFACE DISTRIBUTIONS -- CONSIDERING INTER-CCD GAP ("CROSS") -- ONE QUADRANT
#####################################################################################

def area_quadrant(radius, crosswidth, tosubtract=0):
    """
    Surface of a quadrant of a circle of radius R - a central cross of width a

    np.abs & tosubtract is only used to find the optimum radii for a given geometry, by minimisation
    """
    R, a = radius, crosswidth
    #
    circle = np.pi * R * R
    cross = (2 * (a * 2 * R)) - (a * a)
    return np.abs(0.25 * (circle - cross) - tosubtract)


def equi_surface_radii_withcross(radius, crosswidth, cells=None, bracketmin=0., verbose=0):
    """
    equi_surface_radii_withcross(radius, crosswidth, cells=None, bracketmin=0., verbose=0)

    Compute the radii of the rings making sure all cells occupy the same area
    """

    if cells is None:
        cells = [1,2,3,4]

    cells = np.array(cells)
    nslices = len(cells)
    ncells = np.sum(cells)
    radii = np.zeros(nslices)

    # Surface of each individual cell = surface of the quadrant / nb of cells
    unit_surface = area_quadrant(radius=radius, crosswidth=crosswidth) / ncells

    if verbose:
        print(f"ncells {ncells}, Unit surface {unit_surface}")

    # inner surface = surface of all rings 'inside' and including the current one=
    inner_surface = 0.

    slice = 0
    attempt = 1
    while slice < nslices:

        slice_area = unit_surface * cells[slice]

        if attempt == 1:
            inner_surface += slice_area

        minim = minimize_scalar(area_quadrant, args=(crosswidth, inner_surface), bracket=(bracketmin, radius))

        if verbose:
            print()
            print(f"     slice {slice}, cells {cells[slice]}, slice area {slice_area}, inner_surf {inner_surface}")
            print(f"     minim {minim}")

        if minim["success"]:
            if minim['x'] > 0.:
                radii[slice] = minim['x']
                bracketmin = minim['x']
                slice += 1
                attempt = 1
            else:
                if verbose: print(f"Minimisation failed, bracketmin {bracketmin} -> {bracketmin + 10}")
                bracketmin += 10
                attempt += 1
        else:
            raise Exception(f"Minimisation failed at slice {slice}")

    return radii


def equi_surface_coordinates_withcross(radius, crosswidth, cells=None, midradius=True, verbose=False,
                                       boost=-1, boostFactor=2):
    """

    Parameters
    ----------
    radius : TYPE
        DESCRIPTION.
    cells : TYPE, optional
        DESCRIPTION. The default is [1,2,3,4].

    midradius : used to compute the radius of the points
        midradius = True : the point is at half the thickness of the slice
                  = False : the point is at the radius where half the surface
                           of the cell is outside, and half inside. This depends
                           on the cell geometry -- NOT IMPLEMENTED

    boost: if >= 0, it points to an annulus (i.e. position in 'cells') to be boosted
           boosting means multiplying the number of field positions in that annulus, i.e. returning
           multiple field positions / cell for that specific annulus

    boostFactor if boost >= 0, boostFactor indicates how many field-positions to return / cell on the selected annulus

    Returns
    -------
    x,y = np.arrays of length = number of cells

    """

    if cells is None:
        cells = [1,2,3,4]

    cells = np.array(cells)
    nslices = len(cells)

    slice_radii = equi_surface_radii_withcross(radius=radius, crosswidth=crosswidth, cells=cells)

    xs, ys = [], []
    nk = np.zeros(nslices, dtype=int)

    inner_radius = 0.
    for slice in range(nslices):
        if midradius:
            point_radius = (slice_radii[slice] + inner_radius) / 2.
        else:
            raise Exception("midradius - False is not implemented")

        gap_span = np.arctan(crosswidth / point_radius)

        slice_span = (np.pi / 2.) - (2. * gap_span)
        #
        # angular span of a cell
        if slice == boost:
            npoints = cells[slice] * boostFactor
        else:
            npoints = cells[slice]
        #
        nk[slice] = npoints

        cell_span = slice_span / npoints
        point_angles = np.array([(gap_span + cell_span / 2. + i * cell_span) for i in range(npoints)])
        xs.append(point_radius * np.cos(point_angles))
        ys.append(point_radius * np.sin(point_angles))

        if verbose:
            print(f"slice {slice} radius {point_radius:.3f} angles {[np.rad2deg(i) for i in point_angles]}")

        inner_radius = slice_radii[slice]

    x1d = np.array([point for aslice in xs for point in aslice])
    y1d = np.array([point for aslice in ys for point in aslice])

    return x1d, y1d, nk


def equi_surface_edges_withcross(radius, crosswidth, cells=None, alledges=False):
    """
    This function computes cell-edges in equi-surface distributions.
    It is only relevant for display purposes.

    alledges = False (default) : the edges at 0 & 90 degrees are not included
    """

    if cells is None:
        cells = [1,2,3,4]

    alledges = {False: 0, True: 1}[alledges]

    cells = np.array(cells)
    nslices = len(cells)

    outer_radii = equi_surface_radii_withcross(radius=radius, crosswidth=crosswidth, cells=cells)

    innerxys, outerxys = [], []

    inner_radius = 0.
    for slice in range(nslices):
        outer_radius = outer_radii[slice]

        mid_radius = (outer_radius + inner_radius) / 2.

        gap_span = np.arctan(crosswidth / mid_radius)

        slice_span = (np.pi / 2.) - (2. * gap_span)
        #
        # angular span of a cell
        cell_span = slice_span / (cells[slice])

        edge_angles = np.array([(gap_span + i * cell_span) for i in range(1 - alledges, cells[slice] + alledges)])

        for angle in edge_angles:
            innerxys.append([inner_radius * np.cos(angle), inner_radius * np.sin(angle)])
            outerxys.append([outer_radius * np.cos(angle), outer_radius * np.sin(angle)])

        inner_radius = outer_radius

    return np.array(innerxys), np.array(outerxys)


###################################
## PORTING ONE TO ALL 4 QUADRANTS
###################################


def oneTo4quadrants(x, y, cells, boost=-1, boostFactor=1):
    """
    oneTo4quadrants(x,y, cells, boost=-1, boostFactor=1)

    Assuming x,y represent coordinates in 1 quadrant of a circle,
    we rotate them to copy them the other 3 quadrants

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    cells : description of the radial distribution of iso-surface cells

    boost: if >= 0, it points to an annulus (i.e. position in 'cells') to be boosted
           boosting means multiplying the number of field positions in that annulus, i.e. returning
           multiple field positions / cell for that specific annulus

    boostFactor if boost >= 0, boostFactor indicates how many field-positions to return / cell on the selected annulus

    Returns
    -------
    x,y: same as input, but rotated by multiples of 90 over all quadrants

    """
    xnp, ynp = np.array(x), np.array(y)

    # Propagate solution to all 4 quadrants, 1 radius at a time  ('slice' is a reserved word)
    xxx, yyy = [], []
    innerPoints = 0

    for c, torus in enumerate(cells):
        if c == boost:
            npoints = torus * boostFactor
        else:
            npoints = torus
        xslice, yslice = xnp[innerPoints:innerPoints + npoints], ynp[innerPoints:innerPoints + npoints]
        for theta in [np.pi / 2. * i for i in range(4)]:
            R = np.matrix([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
            xrot, yrot = R @ [xslice, yslice]
            xxx.extend(np.array(xrot)[0, :])
            yyy.extend(np.array(yrot)[0, :])

        innerPoints += npoints

    return np.array(xxx), np.array(yyy)

#########################################
## FULL FOV GEOMETRY PREPARATION COMBINED
#########################################


def equi_surface_fov_geometry(cells, boost, boostFactor, distorted=True, setup=None, verbose=False):

    FOV_SETTINGS = Settings.load("Field-Of-View")
    focal_lenth_mm = FOV_SETTINGS["FOCAL_LENGTH"]
    distortion_coeff = FOV_SETTINGS["DISTORTION_COEFFICIENTS"]

    if setup is None:
        setup = GlobalState.setup

    fee_side = setup.camera.fee.ccd_sides.enum

    # Boundary between E&F side
    col_end = setup.camera.fee.col_end

    # Average Gap between CCDs in mm
    # a = gap = np.mean(np.abs(GlobalState.setup.camera.ccd.origin_offset_xfp)) * 2.
    a = gap = 2.4

    # Radius of the FoV in degrees
    radiusdeg = setup.camera.fov.radius_degrees
    #radiusdeg = 18.87

    # Plate scale: pixel size in arcsec
    pixelsizesec = 15
    # physical size of the pixels
    pixelsizemm = 0.018

    # Radius of the FoV in mm
    R = radiusmm = setup.camera.fov.radius_mm
    # R = radiusmm = radiusdeg * 3600 / pixelsizesec * pixelsizemm  # 81.5184

    x1o, y1o, nps = equi_surface_coordinates_withcross(radius=R, crosswidth=a, cells=cells, midradius=True,
                                                       verbose=False,
                                                       boost=boost, boostFactor=boostFactor)

    x1d, y1d = oneTo4quadrants(x1o, y1o, cells, boost=boost, boostFactor=boostFactor)

    angles = np.array([focal_plane_coordinates_to_angles(xx, yy) for xx, yy in zip(x1d, y1d)])
    # print(f"angles {angles}")

    if distorted:
        disxys = np.array([undistorted_to_distorted_focal_plane_coordinates(xx, yy, distortion_coeff, focal_lenth_mm) for xx, yy in zip(x1d, y1d)])
        x1d, y1d = disxys[:, 0], disxys[:, 1]

    ccdxys = np.array([focal_plane_to_ccd_coordinates(xx, yy) for xx, yy in zip(x1d, y1d)])
    ccdrows, ccdcols, ccd_codes = ccdxys[:, 0], ccdxys[:, 1], np.array(ccdxys[:, 2],dtype=int)

    ccd_side_hash = {True: fee_side.LEFT_SIDE.name, False: fee_side.RIGHT_SIDE.name}
    side_tmp = np.zeros_like(ccd_codes)
    side_tmp[np.where(ccdcols <= col_end)] = True
    ccd_sides = np.array([ccd_side_hash[i] for i in side_tmp])

    if verbose:
        print_fp_and_ccd_coordinates(x1d, y1d, angles, ccdxys, ccd_sides)

    return ccdrows, ccdcols, ccd_codes, ccd_sides, angles


def circle_fov_geometry(n, radius, offset=0.5, cam='n', distorted=True, verbose=False):
    """
    n : nb of fov points to visit on the circle
    radius : boresight angle of all the fov positions to define
    offset : offset in azimuth wrt starting at azimuth 0.
             The offset is specified in units of the azimuthal difference between 2 consecutive points
             The default = 0.5, keeping the points closest to the edge of the CCDs at equal distance from the gap.
    cam = 'n' or 'f' : normal of fast camera
    verbose : debug prints or not
    """
    FOV_SETTINGS = Settings.load("Field-Of-View")
    focal_lenth_mm = FOV_SETTINGS["FOCAL_LENGTH"]
    distortion_coeff = FOV_SETTINGS["DISTORTION_COEFFICIENTS"]

    setup = GlobalState.setup

    fee_side = setup.camera.fee.ccd_sides.enum
    # Boundary between E&F side
    col_end = setup.camera.fee.col_end

    angles = circleFieldAngles(n=n, radius=radius, offset=offset, cam=cam, verbose=verbose)

    thetas, phis = angles[:, 0], angles[:, 1]

    xys = np.array([angles_to_focal_plane_coordinates(t,p) for t,p in zip(thetas, phis)])
    x1d,y1d = xys[:,0],xys[:,1]

    if distorted:
        disxys = np.array([undistorted_to_distorted_focal_plane_coordinates(xx, yy, distortion_coeff, focal_lenth_mm) for xx, yy in zip(x1d, y1d)])
        x1d, y1d = disxys[:, 0], disxys[:, 1]

    ccdxys = np.array([focal_plane_to_ccd_coordinates(xx, yy) for xx, yy in zip(x1d, y1d)])
    ccdrows, ccdcols, ccd_codes = ccdxys[:, 0], ccdxys[:, 1], np.array(ccdxys[:, 2], dtype=int)

    ccd_side_hash = {True: fee_side.LEFT_SIDE.name, False: fee_side.RIGHT_SIDE.name}
    side_tmp = np.zeros_like(ccd_codes)
    side_tmp[np.where(ccdcols <= col_end)] = True
    ccd_sides = np.array([ccd_side_hash[i] for i in side_tmp])

    if verbose:
        print_fp_and_ccd_coordinates(x1d, y1d, angles, ccdxys, ccd_sides)

    return ccdrows, ccdcols, ccd_codes, ccd_sides, angles


def fov_geometry_from_table(distorted=True, distorted_input=True, table_name='reference_full_40', use_angles=True, setup=None, verbose=False):
    """
    INPUT :
        . XY focal plane coordinates, taken from setup.measures.hartmann_plane.input_focal_plane_coordinates
        . distorted = 'distored output' : include optical distortion in the computation of the output CCD coordinates
        . distorted_input = True : the focal plane coordinates given upon input were measured, i.e. they are already affected by optical distorsions
        . table_name in ['reference_single', 'reference_full_40', 'reference_circle_20']
        . use_angles = True : [theta, phi] are read from the table [elevation, azimuth, in degrees]
                     = False : x,y are read from the table [focal plane coordinates, in mm]
    """
    if setup is None:
        setup = GlobalState.setup

    inverse_distortion_coeffs = setup.camera.fov.inverse_distortion_coefficients
    focal_length_mm = setup.camera.fov.focal_length_mm

    if setup is None:
        print("ERROR: the table of x-y focal-plane coordinates is read from the setup")
        return None

    tab = setup.fov_positions[table_name]
    if use_angles:
        thetas,phis = tab['theta'], tab['phi']
        angles = np.vstack([thetas,phis]).T
    else:
        x1d,y1d = tab['x'], tab['y']

        # # LDO measured focal plane coordinates
        # x1d = setup.measures.hartmann_plane.input_focal_plane_coordinates.x
        # y1d = setup.measures.hartmann_plane.input_focal_plane_coordinates.y

        if distorted_input:
            xxyy = np.array([distorted_to_undistorted_focal_plane_coordinates(xx,yy,inverse_distortion_coeffs, focal_length=focal_length_mm) for xx,yy in zip(x1d,y1d)])
            x1d = xxyy[:,0]
            y1d = xxyy[:,1]

        angles = np.array([focal_plane_coordinates_to_angles(x, y) for (x, y) in zip(x1d, y1d)])

    ccdrows, ccdcols, ccd_codes, ccd_sides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

    return ccdrows, ccdcols, ccd_codes, ccd_sides, angles


###################################################
## CONVENIENCE FUNCTION : Sort vs phi in [-180,180[
###################################################

def sort_on_azimuth(angles, arraylist, reverse=False, return_order=False):
    """
    SYNOPSIS
    sort_on_azimuth(angles, arraylist)

    GOAL
    Express all 'angles' in [-180, 180[
    Sort 'angles' in growing order
    Reorder all arrays in 'arraylist' accordingly

    INPUT
    angles, arraylist : see "GOAL"
            angles : 2D array of dimensions n x 2
            arraylist : either 1D, or 2D arrays of dimensions n x 2

    reverse: if True, the order is inverted

    return_order : if True, the sorting order is returned  (based on np.argsort)

    EXAMPLE
    boresight_angle,n_pos = 6.85,20
    ccdrows, ccdcols, ccd_codes, ccd_sides, angles = circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=False)
    angles, [ccdrows, ccdcols, ccd_codes, ccd_sides] = sort_on_azimuth(angles, [ccdrows, ccdcols, ccd_codes, ccd_sides])

    """

    theta, phi = angles[:,0], angles[:,1]

    # 1. Express all phis in [-180, 180[
    phi = phi % 360.
    selhigh = np.where(phi > 180.)
    phi[selhigh] = phi[selhigh] - 360.
    sellow = np.where(phi <= -180.)
    phi[sellow] = phi[sellow] - 360.

    sortsel = np.argsort(phi)

    if reverse:
        sortsel = sortsel[::-1]

    # 2. Sort the arrays in arraylist according to phis

    sortedlist = []
    for array in arraylist:

        try:
            array = np.array(array)
        except:
            print(f"CRITICAL: Problematic input list: {array}")
            raise Abort("sort_on_azimuth: list in 'arraylist' can't be cast into np.array")

        if len(array.shape)==1:
            sortedlist.append(array[sortsel])
        elif len(array.shape)==2:
            out = np.zeros_like(array)
            out[:,0] = array[sortsel,0]
            out[:,1] = array[sortsel,1]
            sortedlist.append(out)
        else:
            print("CRITICAL: function sort_on_azimuth only accepts 1D and 2D arrays in 'arraylist'")
            raise NotImplementedError

    # 3. Sort the input angles
    sortedangles = np.zeros_like(angles)
    sortedangles[:,0] = theta[sortsel]
    sortedangles[:,1] = phi[sortsel]

    if return_order:
        return sortedangles,sortedlist,sortsel
    else:
        return sortedangles, sortedlist


##################################################
## CONVENIENCE FUNCTION : FOV ANGLES -> CCD COORDS
##################################################

def ccd_coordinates_to_angles(ccdrows, ccdcols, ccdcodes, verbose=False):
    """
    INPUT
    ccdrows, ccdcols : target [y,x] CCD coordinates
    ccdcodes : CCD identifyers / position, in [1,2,3,4]
    ccdsides : CCD sides / position, in 'E', 'F'

    OUTPUT
    Field angles theta, phi / position (boresight angle, azimuth)
    """
    setup = GlobalState.setup

    inverse_distortion_coeffs = setup.camera.fov.inverse_distortion_coefficients
    focal_length_mm = setup.camera.fov.focal_length_mm

    fpcoords = np.array(
        [ccd_to_focal_plane_coordinates(row=ccdrow, column=ccdcol, ccd_code=ccdcode) for ccdrow, ccdcol, ccdcode in
         zip(ccdrows, ccdcols, ccdcodes)])

    xxyy = np.array([distorted_to_undistorted_focal_plane_coordinates(xx, yy, inverse_distortion_coeffs,
                    focal_length=focal_length_mm) for xx, yy in zip(fpcoords[:,0], fpcoords[:,1])])

    angles = np.array([focal_plane_coordinates_to_angles(xx, yy) for xx, yy in zip(xxyy[:,0], xxyy[:,1])])

    return angles


def angles_to_ccd_coordinates(angles, distorted=True, verbose=True):
    """
    angles_to_ccd_coords(angles, distorted=True)

    INPUT
    angles : [n,2] array of FoV angles theta (boresight angle), phi (azimuth)
    distorted : introduce the optical distortion in the output

    OUTPUT
    ccdrows, ccdcols, ccd_codes, ccd_sides
         1D arrays of length n, with ccd coordinates ccdrows,ccdcols
    """

    setup = GlobalState.setup
    fee_side = setup.camera.fee.ccd_sides.enum

    distortion_coeff = setup.camera.fov.distortion_coefficients
    focal_lenth_mm = setup.camera.fov.focal_length_mm

    # Boundary between E&F side
    col_end = setup.camera.fee.col_end

    thetas, phis = angles[:, 0], angles[:, 1]

    xys = np.array([angles_to_focal_plane_coordinates(t,p) for t,p in zip(thetas, phis)])
    x1d,y1d = xys[:,0],xys[:,1]

    if distorted:
        disxys = np.array([undistorted_to_distorted_focal_plane_coordinates(xx, yy, distortion_coeff, focal_lenth_mm) for xx, yy in zip(x1d, y1d)])
        x1d, y1d = disxys[:, 0], disxys[:, 1]

    ccdxys = np.array([focal_plane_to_ccd_coordinates(xx, yy) for xx, yy in zip(x1d, y1d)])
    ccdrows, ccdcols = ccdxys[:, 0], ccdxys[:, 1]
    ccd_codes = [int(tmp) if tmp else None for tmp in ccdxys[:, 2]]

    ccd_side_hash = {True: fee_side.LEFT_SIDE.name, False: fee_side.RIGHT_SIDE.name}
    side_tmp = np.zeros_like(ccd_codes)
    side_tmp[np.where(ccdcols.astype(float) <= col_end)] = True # typecasting to float to allow operation on None values.
    ccd_sides = np.array([ccd_side_hash[i] for i in side_tmp])

    if verbose:
        print_fp_and_ccd_coordinates(x1d, y1d, angles, ccdxys, ccd_sides)

    return ccdrows, ccdcols, ccd_codes, ccd_sides


###################################
## FOV REPRESENTATION
###################################


def plotFPA(figname=None, figsize=None, **kwargs):
    import matplotlib.pyplot as plt
    # from matplotlib.patches import Rectangle

    if not 'color' in kwargs.keys(): kwargs['color'] = 'k'
    if not 'lw' in kwargs.keys(): kwargs['lw'] = 1
    if not 'fill' in kwargs.keys(): kwargs['fill'] = False

    ccdSize = 81.18  ## mm
    offset = 1.3  ## mm
    plt.figure(figname, figsize=figsize)
    # lower left
    rectll = plt.Rectangle((-ccdSize - offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectll)
    # top right
    recttr = plt.Rectangle((offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttr)
    # top left
    recttl = plt.Rectangle((-ccdSize - offset, offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(recttl)
    # lower right
    rectlr = plt.Rectangle((offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
    plt.gca().add_patch(rectlr)

    plt.axis('equal')
    plt.xlim(-80, 140)
    plt.ylim(-100, 100)

    circle = plt.Circle((128, 0), radius=5, **kwargs)
    plt.gca().add_patch(circle)

    return


def plotCCDs(figname=None, figsize=(10,10), setup=None, **kwargs):
    import matplotlib.pyplot as plt

    if not 'color' in kwargs.keys(): kwargs['color'] = 'k'
    if not 'lw' in kwargs.keys(): kwargs['lw'] = 1
    if not 'fill' in kwargs.keys(): kwargs['fill'] = False

    if setup is None:
        setup = GlobalState.setup

    plt.figure(figname, figsize=figsize)

    if setup is None:
        #origin_x = origin_y = [1.3,1.3,1.3,1.3]  ## mm

        offset = 1.3
        ccdSize = 81.18  ## mm

        # CCD1 top left
        recttl = plt.Rectangle((-ccdSize - offset, offset), ccdSize, ccdSize, **kwargs)
        plt.gca().add_patch(recttl)
        # CCD2 lower left
        rectll = plt.Rectangle((-ccdSize - offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
        plt.gca().add_patch(rectll)
        # CCD3 lower right
        rectlr = plt.Rectangle((offset, -ccdSize - offset), ccdSize, ccdSize, **kwargs)
        plt.gca().add_patch(rectlr)
        # CCD4 top right
        recttr = plt.Rectangle((offset, offset), ccdSize, ccdSize, **kwargs)
        plt.gca().add_patch(recttr)

    else:
        # compute the FP coordinates of the corners of the CCDs via ccd_to_focal_plane_coordinates

        #origin_x = setup.camera.ccd.origin_offset_x
        #origin_y = setup.camera.ccd.origin_offset_y
        orientation = setup.camera.ccd.orientation
        ccdSize = setup.camera.ccd.pixel_size / 1000. * 4510.

        # CCD1 top left
        origin_x, origin_y = ccd_to_focal_plane_coordinates(row=4510, column=4510, ccd_code=1)
        recttl = plt.Rectangle((origin_x,origin_y), ccdSize, ccdSize, angle=orientation[0]-180., **kwargs)
        plt.gca().add_patch(recttl)
        plt.plot([origin_x+ccdSize/2.,origin_x+ccdSize/2.],[origin_y,origin_y+ccdSize],'k--',alpha=0.25)
        # CCD2 lower left
        origin_x, origin_y = ccd_to_focal_plane_coordinates(row=0, column=4510, ccd_code=2)
        rectll = plt.Rectangle((origin_x,origin_y), ccdSize, ccdSize, angle=orientation[1]-270., **kwargs)
        plt.gca().add_patch(rectll)
        plt.plot([origin_x,origin_x+ccdSize],[origin_y+ccdSize/2.,origin_y+ccdSize/2.],'k--',alpha=0.25)
        # CCD3 lower right
        origin_x, origin_y = ccd_to_focal_plane_coordinates(row=0, column=0, ccd_code=3)
        rectlr = plt.Rectangle((origin_x,origin_y), ccdSize, ccdSize, angle=orientation[2], **kwargs)
        plt.gca().add_patch(rectlr)
        plt.plot([origin_x+ccdSize/2.,origin_x+ccdSize/2.],[origin_y,origin_y+ccdSize],'k--',alpha=0.25)
        # CCD4 top right
        origin_x, origin_y = ccd_to_focal_plane_coordinates(row=4510, column=0, ccd_code=4)
        recttr = plt.Rectangle((origin_x,origin_y), ccdSize, ccdSize, angle=orientation[3]-90.0, **kwargs)
        plt.gca().add_patch(recttr)
        plt.plot([origin_x,origin_x+ccdSize],[origin_y+ccdSize/2.,origin_y+ccdSize/2.],'k--',alpha=0.25)

    plt.xlim(-82, 82)
    plt.ylim(-82, 82)
    plt.axis('equal')

    plt.xlabel("X [mm]", size=14)
    plt.ylabel("Y [mm]", size=14)

    circle = plt.Circle((0,0),radius=82.5, alpha=0.15, **kwargs)
    plt.gca().add_patch(circle)
    circle = plt.Circle((0,0),radius=83, alpha=0.15, **kwargs)
    plt.gca().add_patch(circle)

    return


def equi_surface_plot_fullquadrant(radius, cells=None, alledges=False, title="Equi-surface full quadrant",
                                   **kwargs):
    from matplotlib.patches import Circle

    if cells is None:
        cells = [1,2,3,4]

    radii = equi_surface_radii_fullquadrant(radius, cells=cells)
    xs, ys = equi_surface_coordinates_fullquadrant(radius, cells=cells)

    ax = plt.subplot(111, aspect=1.)
    ax.scatter(xs, ys, c='k')
    plt.xlim(0, radius)
    plt.ylim(0, radius)

    kwargs.setdefault("linestyle", "--")
    kwargs.setdefault("linewidth", "1")

    # CIRCLES
    for r in radii:
        circle = Circle((0, 0), r, edgecolor=(0.5, 0.5, 0.5), facecolor="none", **kwargs)
        ax.add_patch(circle)

    # Outer circle
    # circle = Circle((0, 0), R, facecolor='none', edgecolor='k', linewidth=1, linestyle="-")
    # ax.add_patch(circle)

    # RADIAL EDGES
    inxys, outxys = equi_surface_edges_fullquadrant(radius, cells=cells, alledges=alledges)

    for edge in range(len(inxys)):
        plt.plot([inxys[edge, 0], outxys[edge, 0]], [inxys[edge, 1], outxys[edge, 1]], c=(0.5, 0.5, 0.5), **kwargs)

    plt.xlabel('[mm]', size=14)
    plt.ylabel('[mm]', size=14)
    plt.title(title)

    return


def equi_surface_plot_withcross(radius, crosswidth, cells=None, boost=-1, boostFactor=2, alledges=False,
                                color='k', title="Equi-surface with cross", **kwargs):
    from matplotlib.patches import Circle, Rectangle

    if cells is None:
        cells = [1, 2, 3, 4]

    radii = equi_surface_radii_withcross(radius, crosswidth=crosswidth, cells=cells)
    xs, ys, nn = equi_surface_coordinates_withcross(radius, crosswidth=crosswidth, cells=cells, boost=boost,
                                                    boostFactor=boostFactor)

    ax = plt.subplot(111, aspect=1.)
    ax.scatter(xs, ys, c=color, **kwargs)
    plt.xlim(0, radius + crosswidth / 2.)
    plt.ylim(0, radius + crosswidth / 2.)

    # kwargs.setdefault("linestyle","--")
    # kwargs.setdefault("linewidth","1")

    # CIRCLES
    for r in radii:
        circle = Circle((0, 0), r, edgecolor=(0.5, 0.5, 0.5), facecolor="none", linestyle="--", linewidth=1)
        ax.add_patch(circle)

    # Outer circle
    # circle = Circle((0, 0), R, facecolor='none', edgecolor='k', linewidth=1, linestyle="-")
    # ax.add_patch(circle)

    # RADIAL EDGES
    inxys, outxys = equi_surface_edges_withcross(radius, crosswidth=crosswidth, cells=cells, alledges=alledges)

    for edge in range(len(inxys)):
        plt.plot([inxys[edge, 0], outxys[edge, 0]], [inxys[edge, 1], outxys[edge, 1]], c=(0.5, 0.5, 0.5),
                 linestyle="--", linewidth=1)

    # CROSS
    rect = Rectangle((0, 0), crosswidth, radius, angle=0.0, facecolor=(0.5, 0.5, 0.5))
    ax.add_patch(rect)
    rect = Rectangle((0, 0), radius, crosswidth, angle=0.0, facecolor=(0.5, 0.5, 0.5))
    ax.add_patch(rect)

    plt.xlabel('[mm]', size=14)
    plt.ylabel('[mm]', size=14)
    plt.title(title)

    return


def print_ccd_coordinates(fov_angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    import builtins
    from rich import box
    from rich.table import Table
    from rich.console import Console

    console = Console(width=140)
    table = Table(title="CCD Coordinates", box=box.ASCII)
    table.add_column("Position", justify="center")
    table.add_column("theta")
    table.add_column("phi")
    table.add_column("row")
    table.add_column("column")
    table.add_column("ccd number", justify="center")
    table.add_column("ccd side", justify="center")

    def colorise(value: float, fmt: str) -> str:
        return f"[red]None[/]" if value is None else fmt.format(value)

    msg = None
    for idx, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(fov_angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
        if msg is None and (crow is None or ccol is None or ccode is None or ccd_side is None):
            msg = textwrap.dedent(
                """\
                Some CCD parameters are None and therefore invalid and they are '[red]red[/]' in the above table.
                It is likely caused by positioning outside of the sensing area. See also focal_plane_to_ccd_coordinates(...).
                """
            )
        table.add_row(f"{idx:2d}",
                      f"{angle[0]:6.2f}", f"{angle[1]:6.2f}",
                      colorise(crow, "{:.2f}"), colorise(ccol, "{:.2f}"),
                      colorise(ccode, "{:.0f}"), colorise(ccd_side, "{}"))

    console.print("\n", table)
    if msg is not None:
        console.print(msg)

def print_fp_and_ccd_coordinates(x1d, y1d, angles, ccdxys, ccd_sides):
    import builtins
    from rich import box
    from rich.table import Table
    from rich.console import Console

    console = Console(width=140)
    table = Table(title="CCD Coordinates", box=box.ASCII)
    table.add_column("Position", justify="center")
    table.add_column("fp_x")
    table.add_column("fp_y")
    table.add_column("theta")
    table.add_column("phi")
    table.add_column("row")
    table.add_column("column")
    table.add_column("ccd number", justify="center")
    table.add_column("ccd side", justify="center")

    def colorise(value: float, fmt: str) -> str:
        return f"[red]None[/]" if value is None else fmt.format(value)

    msg = None
    for idx, (xx, yy, angle, ccdxy, ccd_side) in enumerate(zip(x1d, y1d, angles, ccdxys, ccd_sides)):
        if msg is None and (ccdxy[0] is None or ccdxy[1] is None or ccdxy[2] is None or ccd_side is None):
            msg = textwrap.dedent(
                """\
                Some CCD parameters are None and therefore invalid and they are '[red]red[/]' in the above table.
                It is likely caused by positioning outside of the sensing area. See also focal_plane_to_ccd_coordinates(...).
                """
            )
        table.add_row(f"{idx:2d}",
                      f"{xx:6.2f}", f"{yy:6.2f}",
                      f"{angle[0]:6.2f}", f"{angle[1]:6.2f}",
                      colorise(ccdxy[0], "{:.2f}"), colorise(ccdxy[1], "{:.2f}"),
                      colorise(ccdxy[2], "{:.0f}"), colorise(ccd_side, "{}"))


    console.print("\n", table)
    if msg is not None:
        console.print(msg)
