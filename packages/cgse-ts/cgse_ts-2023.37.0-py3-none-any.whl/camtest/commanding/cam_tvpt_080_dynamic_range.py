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
    2023 04 04 - 0.6 Change CCD readout order to a single CCD

"""
import logging

from camtest import building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.functions.make_dither_offset import make_dither_offsets
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_080(mag_list = None, num_frames = None, num_subpix = None, fov_list = None):
    """
    SYNOPSIS
    cam_tvpt_080(mag_list = [4, 7, 8, 9, 11, 16], num_frames = 100, num_subpix = 25, fov_list = [[4, 45], [14, 45], [4, 135], [14, 135], [4, 225], [14, 225], [4, 315], [14, 315]])

    Acquisition for different intensities
        - in each FoV position all sub-pixel positions
        - in each sub-pixel positions a total of num_frames images

    EXAMPLE
    $ execute(cam_tvpt_080, mag_list = [4, 6, 7], num_frames = 100, num_subpix = 10, fov_list = None)
    $ execute(cam_tvpt_080, mag_list = [4, 7, 8, 9, 11, 16], num_frames = 10, num_subpix = 10, fov_list = [[4,45], [14,45]])

    """

    # A. CHECK STARTING CONDITIONS

    # SYSTEM IS IDLE : check system_is_idle, and raise appropriate exception if not
    system_test_if_idle()

    """
    # A. CHECK STARTING CONDITIONS
    if not (dpu.n_cam_is_standby_mode() or dpu.n_cam_is_dump_mode()):
        raise Abort(
            "The N-FEE should be in standby mode at the start of a test. "
            "Verify the status of the N-FEE and make sure it is in STANDBY mode."
        )
    """

    # B. DEFINITION TEST PARAMETERS

    if fov_list is None:
        fov_list = [[4, 45], [14, 45], [4, 135], [14, 135], [4, 225], [14, 225], [4, 315], [14, 315]]

    # visit only one FoV position if the test needs more than two days for all 8 FoV positions
    if len(mag_list) * num_frames * num_subpix * len(fov_list) * 25 / 3600 / 24 > 2:
        fov_list = [[14, 45]]

    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(fov_list, distorted = True, verbose = True)

    # C. COMMANDING

    ogse.shutter_open()

    for posid, fov in zip(range(len(fov_list)), fov_list):

        for mag in mag_list:

            # translation of magnitude to attenuation with the assumption that mag 8 corresponds to 100% full well
            ogse.set_fwc_fraction(fwc_fraction=pow(10, 0.4 * (8 - mag)))
            delta_theta, delta_phi = make_dither_offsets(num_subpix)

            visit_field_angles(fov[0], fov[1])

            for s in range(num_subpix):

                point_source_to_fov(theta=fov[0] + delta_theta[s], phi=fov[1] + delta_phi[s], wait=True)
                dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_frames, ccd_order=[ccdcodes[posid], ccdcodes[posid], ccdcodes[posid], ccdcodes[posid]],
                                       ccd_side=ccdsides[posid], rows_overscan=30)


    ogse.shutter_close()

    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_tvpt_080_dynamic_range")
