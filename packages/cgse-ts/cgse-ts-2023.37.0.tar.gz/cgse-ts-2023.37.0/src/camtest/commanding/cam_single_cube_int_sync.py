"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.1 CAM-TVPT-010 Camera best focus determination

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Shutter closed
    CAM in DUMP mode
    OGSE attenuation set [to get a decent signal i.e. min a few thousand a.d.u. with the exposure_time commanded here]

End status
    Shutter closed
    CAM in DUMP mode

Synopsis:
    - go to the selected position in the FoV
    - acquire a single cube of images at that location
    - image acquisition:
        n_cycles
        partial readout of 'n_rows'
        internal sync, with "exposure_time"

Authors: P. Royer

Versions:
    2021 11 12 - 0.1 Creation
"""
import logging

import numpy as np
import time

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)

@building_block
def cam_single_cube_int_sync(theta=None, phi=None, num_cycles=None, exposure_time=None, n_rows=None, attenuation=None):
    """

    SYNOPSIS
    cam_single_cube_int_sync(theta=None, phi=None, num_cycles=None, exposure_time=None, n_rows=None, attenuation=None)

    INPUTS
    theta,phi     : FoV location, i.e. [boresight_angle, azimuth], in degrees
    num_cycles    : int, nb of images acquired at every single dither position
    exposure_time : float, effective exposure time. The cycle_time is computed from it
                    (cycle_time = exposure_time + readout_time)
    n_rows        : int, nb of rows to be readout around the expected source position (e.g. 500 = 250 below, 250 above)
    attenauation  : fwc_fraction, will be used to command the ogse

    EXAMPLES
    $ execute(cam_single_cube_int_sync, theta=8.3, phi=-9, num_cycles=5, exposure_time=1., n_rows=1000, attenuation=1.)

    """
    LOGGER.info("START: cam_single_cube_int_sync")

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    #  FEE READY ?
    ####################################################

    while (dpu.n_cam_is_ext_sync()):
        time.sleep(1.)

    ####################################################
    #  OGSE ATTENUATION
    ####################################################

    LOGGER.info(f"Setting OGSE fwc_fraction to {attenuation=}")
    ogse.set_fwc_fraction(fwc_fraction=attenuation)
    time.sleep(1.)
    while (ogse.attenuator_is_moving()):
        time.sleep(1.)

    ####################################################
    #  POINTING
    ####################################################

    LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
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
    #  IMAGE ACQUISITION
    ####################################################

    # Acquire background images:
    LOGGER.info(f"Acquiring Background frames for the FoV position ({theta}, {phi})")

    ogse.shutter_open()

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["row_start"] = max(0, ccdrows[0] - n_rows // 2)
    n_fee_parameters["row_end"] = min(4509, ccdrows[0] + n_rows // 2)
    n_fee_parameters["rows_final_dump"] = 4510
    n_fee_parameters["ccd_order"] = [ccdcodes[0], ccdcodes[0], ccdcodes[0], ccdcodes[0]]
    n_fee_parameters["ccd_side"] = ccdsides[0]
    n_fee_parameters["exposure_time"] = exposure_time

    dpu.n_cam_partial_int_sync(**n_fee_parameters)

    ogse.shutter_close()

    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_single_cube_int_sync")
