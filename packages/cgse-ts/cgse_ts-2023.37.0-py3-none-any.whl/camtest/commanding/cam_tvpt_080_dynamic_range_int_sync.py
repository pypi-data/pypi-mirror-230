"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.7 CAM-TVPT-080 Dynamic range

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in STANDBY

End status
    NFEE in STANDBY

Synopsis:
    - Set different intensities (magnitudes)
        - visit all FoV positions
            visit all sub-pixel positions
            Acquire TBD (100?) images

Authors: C. Paproth

Versions:
    2021 03 26 - 0.1 Draft -- Creation (based on cam_tvpt_010_best_focus_determination.py written by M. Pertenais)
    2021 07 07 - 0.2 Update after test rehearsal
    2021 10 26 - 0.3 Update to reduce time needed for the test
    2021 11 03 - 0.4 Update to reduce FoV positions if test needs too much time
    2022 04 26 - 0.5 Open shutter
    2023 04 03 - 0.6 Use internal sync
    2023 04 27 - 0.7 Make exposure time a parameter of the script

"""
import logging

import time
from camtest import building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.dpu import wait_cycles
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.functions.make_dither_offset import make_dither_offsets
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_080_int_sync(mag_list = None, num_frames = None, num_subpix = None, num_bck = None, exposure_time = None, fov_list = None):
    """
    SYNOPSIS
    cam_tvpt_080_int_sync(mag_list = [4, 7, 8, 9, 11, 16], num_frames = 100, num_subpix = 25, num_bck = 3, exposure_time = 0.1, fov_list = [[4, 45], [14, 45], [4, 135], [14, 135], [4, 225], [14, 225], [4, 315], [14, 315]])

    Acquisition for different intensities with an exposure time of exposure_time
        - in each FoV position num_bck dark frames
        - in each FoV position all sub-pixel positions
        - in each sub-pixel positions a total of num_frames images

    EXAMPLE
    $ execute(cam_tvpt_080_int_sync, mag_list = [4, 6, 7], num_frames = 100, num_subpix = 10, num_bck = 3, exposure_time = 0.1, fov_list = None)
    $ execute(cam_tvpt_080_int_sync, mag_list = [4, 7, 8, 9, 11, 16], num_frames = 10, num_subpix = 10, num_bck = 3, exposure_time = 0.1, fov_list = [[4,45], [14,45]])

    """

    # A. CHECK STARTING CONDITIONS

    # SYSTEM IS IDLE : check system_is_idle, and raise appropriate exception if not
    system_test_if_idle()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    while (dpu.n_cam_is_ext_sync()):
        time.sleep(1.)

    # B. DEFINITION TEST PARAMETERS

    if fov_list is None:
        fov_list = [[4, 45], [14, 45], [4, 135], [14, 135], [4, 225], [14, 225], [4, 315], [14, 315]]
    
    hclearout = {True: 4510, False: 0}
    n_rows = 400
    clearout = True
    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(fov_list, distorted = True, verbose = True)

    # C. COMMANDING

    for posid, fov in zip(range(len(fov_list)), fov_list):

        if ccdrows[posid] is None or ccdcols[posid] is None or ccdcodes[posid] is None or ccdsides[posid] is None:
            LOGGER.warning(f"Invalid Selected Field Positions:\n {fov}")
            continue

        theta0 = fov[0]
        phi0 = fov[1]

        point_source_to_fov(theta = theta0, phi = phi0, wait = True)
        visit_field_angles(theta0, phi0)

        # Acquire background images:
        LOGGER.info(f"Acquiring Background frames for the FoV position ({theta0}, {phi0})")

        n_fee_parameters = dict()
        n_fee_parameters["num_cycles"] = num_bck
        n_fee_parameters["row_start"] = max(0, ccdrows[posid] - n_rows//2)
        n_fee_parameters["row_end"] = min(4509, ccdrows[posid] + n_rows//2)
        n_fee_parameters["rows_final_dump"] = hclearout[clearout]
        n_fee_parameters["ccd_order"] = [ccdcodes[posid], ccdcodes[posid], ccdcodes[posid], ccdcodes[posid]]
        n_fee_parameters["ccd_side"] = ccdsides[posid]

        dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time = exposure_time)

        # Start infinite loop of acquisition
        LOGGER.info(f"Acquiring Images for the FoV position ({theta0}, {phi0})")
        ogse.shutter_open()

        for mag in mag_list:

            # translation of magnitude to attenuation with the assumption that mag 8 corresponds to 100% full well
            ogse.set_fwc_fraction(fwc_fraction = pow(10, 0.4 * (8 - mag)))
            delta_theta, delta_phi = make_dither_offsets(num_subpix)

            n_fee_parameters["num_cycles"] = 0
            dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time = exposure_time)

            for s in range(num_subpix):
                wait_cycles(num_frames)
                theta = theta0 + delta_theta[s]
                phi = phi0 + delta_phi[s]
                dpu.on_long_pulse_do(point_source_to_fov, theta = theta, phi = phi, wait = False)

            wait_cycles(num_frames)     # this for the last dither position

            # num_cycles = 0 --> explicit commanding of dump_mode_int_sync
            dpu.n_cam_to_dump_mode_int_sync()

        ogse.shutter_close()

  
    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_tvpt_080_dynamic_range_int_sync")
