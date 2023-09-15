"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR THE CALIBRATION OF THE OGSE ATTENUATION FACTORS

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
    2020 10 28 : Creation

"""
import logging

import time

import numpy as np

from camtest.commanding import ogse, dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


def cam_gcal_010_ogse_attenuation_cal_int_sync(num_cycles=None, exposure_times=None, theta=None, phi=None, n_rows=None, levels=None):
    """
    SYNOPSIS
    cam_gcal_010_ogse_attenuation_cal_int_sync(num_cycles=None, exposure_time=None, theta=None, phi=None, n_rows=None, levels=None)

    GOAL
    - go to a given FoV position defined by [theta,phi] = [boresight angle, azimuth] (degrees)
    - visit all ogse attenuator indices (levels = None) or a given set of them (levels = [list of indices])
    - at each level, acquire internal sync images at different exposure times, given in the list 'exposure_times'


    INPUTS
    num_cycles = 5: nb of images to be acquired at every FoV position
    exposure_times: list of desired exposure times (the image cycle_time is computed from the exposure_time)
    theta, phi    : boresight_angle (elevation) and azimuth of the reference position for all measures
    n_rows=1000   : nb of rows to read (partial readout). n_rows//2 above and below the computed source position
    levels        : list of OGSE attenuator indices to visit
                    if 'None' or 'False', all indices are visited
    """

    # setup = GlobalState.setup

    # Time granularity for checking upon the OGSE status
    time_granularity = 0.5

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
    # GO TO REFERENCE FOV POSITION
    ####################################################

    point_source_to_fov(theta=theta, phi=phi, wait=True)
    visit_field_angles(theta, phi)

    ####################################################
    # CORRESPONDING CCD PIXEL COORDINATES
    ####################################################

    fov_angles = np.array([[theta, phi]])

    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(fov_angles, distorted=True, verbose=True)

    LOGGER.info(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
    c = 0
    for angle, crow, ccol, ccode, ccd_side in zip(fov_angles, ccdrows, ccdcols, ccdcodes, ccdsides):
        LOGGER.info(
            f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
        c += 1

    ####################################################
    # NB OF FLUX LEVELS
    ####################################################

    if not levels:

        n_levels = len(ogse.get_relative_intensity_by_index().keys())
        levels = range(n_levels)

    ####################################################
    # CORE OF THE TEST
    ####################################################

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["row_start"] = max(0, ccdrows[0] - n_rows // 2)
    n_fee_parameters["row_end"] = min(4509, ccdrows[0] + n_rows // 2)
    n_fee_parameters["rows_final_dump"] = 4510
    n_fee_parameters["ccd_order"] = [ccdcodes[0], ccdcodes[0], ccdcodes[0], ccdcodes[0]]
    n_fee_parameters["ccd_side"] = ccdsides[0]

    for level in levels:

        # SET OGSE ATTENUATOR TO NEXT LEVEL
        ogse.set_attenuator_index(level)

        c = 0
        while not ogse.attenuator_is_ready():

            if not c%10:
                LOGGER.info(f"Waiting for OGSE attenuator to be ready")

            time.sleep(time_granularity)

        # ACQUIRE FRAMES WITH ALL REQUESTED EXPOSURE TIMES
        for exposure_time in exposure_times:

            LOGGER.info(f"OGSE att index {level} - {exposure_time=}")

            dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
