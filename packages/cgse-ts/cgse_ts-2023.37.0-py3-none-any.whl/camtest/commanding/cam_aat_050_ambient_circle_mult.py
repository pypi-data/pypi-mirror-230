"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR HARTMANN VERIFICATION TEST AT AMBIENT, OVER A SET OF POSITIONS AT A FIXED BORESIGHT ANGLE

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    CAM in DUMP mode or DUMP mode internal sync

End status
    CAM in DUMP mode internal sync
    MGSE with the source at the last visited FoV position

Synopsis:

Authors: P. Royer

Versions:
    2020 10 27 : Creation from cam_aat_050_ambient_hartmann_recentering_prep [ran multiple times in CSL at EM level]


"""
import logging

from camtest import building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_to_idle, system_test_if_idle
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from egse.exceptions import Abort

LOGGER = logging.getLogger(__name__)


@building_block
def cam_aat_050_ambient_circle_mult(num_cycles=None, exposure_time=None, elevations=None, n_poss=None, n_rows=None, alternate_order=None):
    """
    SYNOPSIS
    cam_aat_050_ambient_circle_mult(num_cycles=None, exposure_time=None, elevations=None, n_pos=None, n_rows=None, alternate_order=None)

    GOAL
    Run
    cam_aat_050_ambient_circle(num_cycles=None, exposure_time=None, elevation=None, n_pos=None, n_rows=None, reverse_order=None)
    for a list or elevations

    Visit the n_pos FoV positions equidistant from each other over a circle at boresight angle 'elevation'
    At every position, acquire num_cycles images, with partial readout of n_rows rows and an exposure time
    of exposure_time

    NB: Values in n_pos must be a multiple of 4 !!

    INPUTS
    num_cycles = 5: nb of images to be acquired at every FoV position
    exposure_time : exposure time, used by the DPU mode for FEE-internal-synchronization to compute the image cycle_time
    elevations    : list of elevations = list of circles to perform
    n_poss        : list of nb of FoV positions to visit. Must be the same length as elevations, or an int.
                    if given as an int, the same value will be used for all circles
    n_rows=1500   : nb of rows to read (partial readout). n_rows//2 above and below the computed source position
    alternate_order : if True, the direction of subsequent circles will be inverted, to gain time

    EXAMPLE:
        cam_aat_050_ambient_circle_mult(num_cycles=5, exposure_time=0.2, elevations=[3.1, 8.3, 12.4, 16.33], n_poss=[4,8,12,16], n_rows=1000, alternate_order=True)
    """

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # VERIFY INPUT PARAMETERS
    if isinstance(n_poss, int):
        n_poss = [n_poss for i in range(len(elevations))]
    elif len(n_poss) != len(elevations):
        raise Abort(f"n_poss must be either int, or a list the same size as 'elevations'. Aborting.")

    for n_pos in n_poss:
        if (n_pos % 4):
            raise Abort(f"{n_pos=}, must be a multiple of 4. Aborting.")
    if alternate_order:
        # True here will be inverted at the start of the loop --> we'll start with False
        reverse_order = True
    else:
        # Set to False in all cases
        reverse_order = False

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    # MAKE SURE THE OGSE SHUTTER IS OPEN
    ogse.shutter_open()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    # FOV GEOMETRY DEFINITION
    ####################################################

    for elevation, n_pos in zip(elevations, n_poss):

        if alternate_order:
            reverse_order = (reverse_order + 1) % 2

        ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
            circle_fov_geometry(n=n_pos, radius=elevation, offset=0.5, cam='n', distorted=True, verbose=True)

        #reverse_order = False
        angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig,
                                                                                      ccdcodesorig, ccdsidesorig],
                                                                         reverse=reverse_order)

        LOGGER.info(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
        c = 0
        for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
            LOGGER.info(
                f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
            c += 1

        ####################################################
        # BUILDING BLOCK EXECUTION
        ####################################################

        LOGGER.info(f"EXECUTION OF CIRCLE : {n_pos} FoV positions; boresight angle {elevation} ")

        cam_aat_050_ambient_recentering(num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
                                        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
                                        n_rows=n_rows)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
