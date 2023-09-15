"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.7 CAM-TVPT-080 Dynamic range - Persistence Crosstalk

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in STANDBY

End status
    NFEE in STANDBY

Synopsis:
    - Put a very bright spot in the middle of CCD1F and CCD2E and acquire several frames
    - Acquire dark frames before and after illumination with the very bright spot

Authors: C. Paproth

Versions:
    2022 05 30 - 0.1 Draft -- Creation


"""

from camtest import building_block
from camtest.commanding import ogse, dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles


@building_block
def cam_tvpt_080_B(mag = None, num_frames = None, num_predark = None, num_postdark = None, fov_list = None):
    """
    SYNOPSIS
    cam_tvpt_080_B(mag = 1, num_frames = 10, num_predark = 10, num_postdark = 50, fov_list = [[15, 145], [10, 205]])

    Acquisition for all fov_list positions
        - num_predark dark images
        - num_frames images with the bright spot of magnitude mag
        - num_postdark dark images

    EXAMPLE
    $ execute(cam_tvpt_080_B, mag = 1, num_frames = 10, num_predark = 10, num_postdark = 50, fov_list = [[15, 145], [10, 205]])

    """

    # A. CHECK STARTING CONDITIONS

    # SYSTEM IS IDLE : check system_is_idle, and raise appropriate exception if not
    system_test_if_idle()

    # B. DEFINITION TEST PARAMETERS

    # C. COMMANDING

    ogse.set_fwc_fraction(fwc_fraction = pow(10, 0.4 * (8 - mag)))

    for fov in fov_list:

        visit_field_angles(fov[0], fov[1])
        point_source_to_fov(theta=fov[0], phi=fov[1], wait=True)

        dpu.on_frame_number_do(dpu.n_cam_full_ccd, num_cycles=num_predark, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                               rows_overscan=30)
        ogse.shutter_open()
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_frames, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                               rows_overscan=30)
        ogse.shutter_close()
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_postdark, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                               rows_overscan=30)

    system_to_idle()
