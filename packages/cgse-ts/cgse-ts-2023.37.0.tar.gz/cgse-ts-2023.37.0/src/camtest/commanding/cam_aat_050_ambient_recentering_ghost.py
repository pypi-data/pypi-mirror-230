"""Camera Test for the optical alignment of the FPA with respect to the TOU.

HIGH LEVEL TEST SCRIPT FOR HARTMANN VERIFICATION TEST AT AMBIENT,
OVER A SET OF POSITIONS AT A FIXED BORESIGHT ANGLE
AT EVERY FOV POSITION THE NOMINAL LOCATION IS VISITED, FOLLOWED BY THE
LOCATION OF THE POINT-LIKE GHOST, ON THE OPPOSITE SIDE OF THE OPTICAL AXIS

History: 20221014. PR. Creation based on cam_aat_050_ambient_recentering
"""

import time
from camtest import dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.mgse import point_source_to_fov
from camtest.core.exec import building_block
from egse.visitedpositions import visit_field_angles
from camtest.commanding import ogse
import logging

LOGGER = logging.getLogger(__name__)

@building_block
def cam_aat_050_ambient_recentering_ghost(num_cycles=None, num_cycles_ghost=None, exposure_time=None, exposure_time_ghost=None, angles=None, ccd_rows=None, ccd_cols=None, ccd_codes=None, ccd_sides=None, n_rows=None, attenuation=None, attenuation_ghost=None):
    """
    SIGNATURE
    cam_aat_050_ambient_recentering_ghost(num_cycles=None, exposure_time=None, exposure_time_ghost=None, angles=None, ccd_rows=None, ccd_cols=None, ccd_codes=None, ccd_sides=None)

    INPUT
    num_cycles      : number of image cycles to be acquired at every position in the FoV
    num_cycles_ghost: number of image cycles to be acquired at the ghost position, i.e. on the complementary CCD
                      if 0 or negative, the ghost will not be visited
    exposure_time   : exposure time [cycle_time will be computed from it]
    exposure_time_ghost: exposure time for the ghost
    angles          : field angles to be visited
                     [theta,phi] (commanding manual)
                     array [n,2] with n = nb of FoV positions to visit
    ccd_rows, ccd_cols, ccd_codes, ccd_sides : (distorted) CCD coordinates corresponding to the FoV positions in 'angles'

    n_rows         : number of rows read (partial readout)

    SYNOPSIS
    Visit each of the FoV positions defined by angles (must correspond to ccd_rows, ccd_cols, ccd_codes, ccd_sides)

    At each of these positions, acquire num_cycle images with an exposure time of "exposure_time".

    The FEEs are operated under partial readout. The region of interest is centered on "angles" and is made of n_rows rows

    """

    # TEST STARTING CONDITIONS (SYSTEM IN IDLE MODE)
    system_test_if_idle()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    #  FEE READY ?
    ####################################################

    while(dpu.n_cam_is_ext_sync()):
        time.sleep(1.)

    # DATA PREPARATION
    ##################

    # FOV Locations
    npos = len(ccd_rows)
    theta_array, phi_array = angles[:,0], angles[:,1]

    if angles.shape[0] != npos:
        print("Size Mismatch in 'angles'")
        return None
    if (len(ccd_sides)!= npos) or (len(ccd_cols)!=npos) or (len(ccd_codes)!=npos):
        print("Size mismatch on CCD coordinates")
        return None

    # CORE OF THE TEST
    ##################

    for pos in range(npos):

        #  OGSE ATTENUATION - Source
        LOGGER.info(f"Setting OGSE fwc_fraction for source: {attenuation=}")
        ogse.set_fwc_fraction(fwc_fraction=attenuation)
        while (ogse.attenuator_is_moving()):
            time.sleep(1.)

        # Move the stages to illuminate pixel (theta, phi)
        theta, phi = theta_array[pos],phi_array[pos]

        point_source_to_fov(theta=theta, phi=phi, wait=True)
        visit_field_angles(theta, phi)

        n_fee_parameters = dict()
        n_fee_parameters["num_cycles"] = num_cycles
        n_fee_parameters["row_start"] = max(0, ccd_rows[pos]-n_rows//2)
        n_fee_parameters["row_end"] = min(4509, ccd_rows[pos]+n_rows//2)
        n_fee_parameters["rows_final_dump"] = 4510
        n_fee_parameters["ccd_order"] = [ccd_codes[pos], ccd_codes[pos], ccd_codes[pos], ccd_codes[pos]]
        # n_fee_parameters["ccd_side"] = [ccd_sides[pos], ccd_sides[pos], ccd_sides[pos], ccd_sides[pos]]
        n_fee_parameters["ccd_side"] = ccd_sides[pos]

        # Acquire images on the prime location

        dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

        dpu.n_cam_to_dump_mode_int_sync()

        # Acquire images on the ghost location (inf. loop not allowed. If 0 frames --> skip the ghost)

        if num_cycles_ghost > 0:

            #  OGSE ATTENUATION - Ghost
            LOGGER.info(f"Setting OGSE fwc_fraction for ghost: {attenuation_ghost=}")
            ogse.set_fwc_fraction(fwc_fraction=attenuation_ghost)
            while(ogse.attenuator_is_moving()):
                time.sleep(1.)

            # Complementary CCD (the ghost is at the opposite location wrt the optical axis)
            ccd_ghost = (ccd_codes[pos] + 2) % 4
            if ccd_ghost == 0:
                ccd_ghost = 4

            n_fee_parameters["num_cycles"] = num_cycles_ghost
            n_fee_parameters["ccd_order"] = [ccd_ghost, ccd_ghost, ccd_ghost, ccd_ghost]

            dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time_ghost)

            dpu.n_cam_to_dump_mode_int_sync()

    #  OGSE ATTENUATION - Reset
    LOGGER.info(f"Resett OGSE fwc_fraction to: {attenuation=}")
    ogse.set_fwc_fraction(fwc_fraction=attenuation)

    # RESET SYSTEM IN STANDARD CONDITIONS, i.e. IDLE MODE
    system_to_idle()
