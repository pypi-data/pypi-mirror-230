"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR HARTMANN VERIFICATION TEST AT AMBIENT, OVER A SET OF POSITIONS AT A FIXED BORESIGHT ANGLE

N-CAM

Start condition:
    Dark conditions in the lab
    OGSE attenuation properly set


End status
    CAM in DUMP mode internal sync
    MGSE with the source at the last visited FoV position
    N-FEE in DUMP mode or DUMP mode internal sync

Synopsis:

Authors: P. Royer

Versions:
    2023 05 16 : Creation


"""
import logging

import numpy as np
from camtest import building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_to_idle, system_test_if_idle
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_aat_050_ambient_ccdedge(num_cycles=None, exposure_time=None, theta=None, phi_range=None, phi_step=None,
                                n_rows=None):
    """

    GOAL
    Visit the n_pos FoV positions equidistant from each other over an arc of a circle at boresight angle 'elevation'
    At every position, acquire num_cycles images, with partial readout of n_rows rows and an exposure time
    of exposure_time

    Important note: The script allows for positions crossing the gap between CCDs

    INPUTS
    num_cycles = 5: nb of images to be acquired at every FoV position
    exposure_time : exposure time, used by the DPU mode for FEE-internal-synchronization to compute the image cycle_time
    theta         : boresight angle to be used
    phi_range     : range of azimuths to be visited. Two elements = [phi_min, phi_max]
    phi_step      : step in azimuth
    n_rows=1500   : nb of rows to read (partial readout). n_rows//2 above and below the computed source position
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

    phis = np.arange(phi_range[0], phi_range[1] + phi_step, phi_step)
    thetas = np.ones_like(phis) * theta
    n_pos = len(thetas)

    hnextccd = {1: 2, 2: 3, 3: 4, 4: 1}
    hprevccd = {1: 4, 2: 1, 3: 2, 4: 3}

    angles = np.vstack([thetas, phis]).T

    ccd_rows, ccd_cols, ccd_codes, ccd_sides = angles_to_ccd_coordinates(angles, distorted=True, verbose=True)

    ccd_codes = np.array(ccd_codes)
    first, second = 0, 0
    for pos in range(n_pos):
        if phis[pos] % 90 > 45:
            # We're not in the gap --> update the first position = where we are now, given that (azimuth % 90) > 45
            if ccd_codes[pos] is not None:
                first = pos
            ccd_row, ccd_col, ccd_code, ccd_side = ccd_rows[first], ccd_cols[first], ccd_codes[first], ccd_sides[first]
            try:
                # Second position = first time we'll visit the next CCD
                second = np.where(ccd_codes == hnextccd[ccd_code])[0][0]
                LOGGER.info(
                    f"{pos=:2d} {first=:2d} {second=:2d} CCD {ccd_codes[first]}->{ccd_codes[second]}  [{theta:.2f},{phis[pos]:7.2f}]")
            except IndexError:
                # The request visits only one CCD
                second = None
                LOGGER.info(
                    f"{pos=:2d} {first=:2d} {second=} CCD {ccd_codes[first]}  [{theta:.2f},{phis[pos]:7.2f}]")
        else:
            # We're not in the gap --> update the second position = where we are now, given that (azimuth % 90) < 45
            if ccd_codes[pos] is not None:
                second = pos
            ccd_row, ccd_col, ccd_code, ccd_side = ccd_rows[second], ccd_cols[second], ccd_codes[second], ccd_sides[
                second]
            try:
                # First position = last time we visited the previous CCD
                first = np.where(ccd_codes == hprevccd[ccd_code])[0][-1]
                LOGGER.info(
                    f"{pos=:2d} {first=:2d} {second=:2d} CCD {ccd_codes[first]}->{ccd_codes[second]}  [{theta:.2f},{phis[pos]:7.2f}]")
            except IndexError:
                # The request visits only one CCD
                first = None
                LOGGER.info(
                    f"{pos=:2d} {first=} {second=:2d} CCD {ccd_codes[second]}  [{theta:.2f},{phis[pos]:7.2f}]")

        # MOVE THE STAGES TO ILLUMINATE (theta, phi)

        point_source_to_fov(theta=theta, phi=phis[pos], wait=True)
        visit_field_angles(theta, phis[pos])

        # ACQUIRE IMAGES
        for idx in [first, second]:
            if idx is not None:
                n_fee_parameters = dict()
                n_fee_parameters["num_cycles"] = num_cycles
                n_fee_parameters["row_start"] = max(0, ccd_rows[idx] - n_rows // 2)
                n_fee_parameters["row_end"] = min(4509, ccd_rows[idx] + n_rows // 2)
                n_fee_parameters["rows_final_dump"] = 4510
                n_fee_parameters["ccd_order"] = [ccd_codes[idx], ccd_codes[idx], ccd_codes[idx], ccd_codes[idx]]
                n_fee_parameters["ccd_side"] = ccd_sides[idx]

                dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

        dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
