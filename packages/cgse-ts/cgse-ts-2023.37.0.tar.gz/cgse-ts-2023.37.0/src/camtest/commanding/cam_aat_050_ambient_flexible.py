"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT TO VISIT ANY SELECTION OF FOV POSITIONS

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
    2021 01 20 : Creation from cam_aat_050_ambient_circle


"""
import logging

import numpy as np
from camtest.commanding import ogse, dpu
from camtest.commanding import system_to_idle, system_test_if_idle
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest import building_block

LOGGER = logging.getLogger(__name__)


@building_block
def cam_aat_050_ambient_flexible(num_cycles=None, thetas=None, phis=None, grid=None, n_rows=None, exposure_time=None):
    """
    SYNOPSIS
    cam_aat_050_ambient_flexible(num_cycles=None, thetas=None, phis=None, grid=None, n_rows=None, exposure_time=None)

    GOAL
    Visit the FoV positions defined by thetas, phis and grid
    At every position, acquire num_cycles images, with partial readout of n_rows rows and an exposure time
    of exposure_time

    INPUTS
    num_cycles = 5: nb of images to be acquired at every FoV position
    thetas, phis  : elevations and azimuths of the FoV positions to visit
    grid          : False : use [thetas, phis] as a simple list of coordinates. The 2 arrays must have the same size
                    True  : make a 2d grid from the input thetas & phis, i.e. visit every phi for every theta
                            (nested loop with phis outside)
    exposure_time : exposure time, used by the DPU mode for FEE-internal-synchronization to compute the image cycle_time
    n_rows=1500   : nb of rows to read (partial readout). n_rows//2 above and below the computed source position

    Example:

        cam_aat_050_ambient_flexible(num_cycles=5, thetas=thetas, phis=phis, grid=True, n_rows=1000, exposure_time=0.2)


    """

    ####################################################
    # STARTING CONDITIONS
    ####################################################

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

    if grid:
        tmp2d = np.meshgrid(thetas, phis)
        thetas = np.ravel(tmp2d[0])
        phis = np.ravel(tmp2d[1])

    angles = np.vstack([thetas, phis]).T

    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles=angles, distorted=True, verbose=True)

    # angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
    #                                                            [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
    #                                                             reverse=reverse_order)

    LOGGER.info(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
    c = 0
    for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
        LOGGER.info(
            f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
        c += 1

    ####################################################
    # OGSE INTENSITY
    ####################################################

    # OGSE attenuation level : 0 = dark; 1 = no attenuation.
    # ogse_attenuation = 1.
    # ogse.set_relative_intensity(relative_intensity=ogse_attenuation)


    ####################################################
    # BUILDING BLOCK EXECUTION
    ####################################################

    cam_aat_050_ambient_recentering(num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
                                    ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
                                    n_rows=n_rows)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
