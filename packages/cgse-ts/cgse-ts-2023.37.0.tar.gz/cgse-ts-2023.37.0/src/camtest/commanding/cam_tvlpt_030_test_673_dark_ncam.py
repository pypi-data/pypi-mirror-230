"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.7.3 CAM-TVLPT-030 short dark current measurement at operational temperature

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Test environment in IDLE state (FEE in dump mode)

End status
    Test environment in IDLE state

Synopsis:
    - FEE to reverse clocking
        Acquire 100 "bias" frames
    - FEE to full image mode
        Acquire 100 full images (200 cycles of 25 sec)

Comments:
    - The expected dark current is ~ 1 adu / frame, which justifies
      the necessity for an extensive set of reference bias frames


Authors: P.Royer; R.Huygen

Versions:
    2020 06 12 - 0.1 Draft -- DPU calls & CCD operational parameters TBC
    2021 05 31 - 0.2 Set ccd_side to BOTH and adopt full standard observing mode for dark

"""

from camtest.commanding import system_test_if_idle, system_to_idle, dpu
from camtest.commanding.dpu import n_cam_reverse_clocking, n_cam_full_standard
from camtest.core.exec import building_block


@building_block
def cam_tvlpt_030(num_bias=None, num_dark=None):
    """
    SYNOPSIS
    cam_tvlpt_030(num_bias=None,num_dark=None)


    1. Acquisition of 'num_bias' full frames, CCDs in reverse clocking
            Reverse clocking scheme : parallel in REV, serial in FWD
            --> provides representative electronic offset and r.o.n.

    2. Acquisigtion of 'num_dark'

    EXAMPLE
    $ execute(cam_tvlpt_030,num_bias=100,num_dark=100)

    """

    # A. CHECK STARTING CONDITIONS
    system_test_if_idle()

    # Generic Parameters for full frame acquisition over all CCDs
    #row_start = 0
    #row_end = 4540
    #col_end = 2295  # Default = 2295; includes serial pre- & overscans
    ccd_order = [1, 2, 3, 4]

    # C. ACQUIRE REFERENCE FULL FRAME "BIAS" FRAMES

    # Reverse-clocking specific parameters
    # Scheme can be 'bilevel', 'trilevel',  'bi-level' = default mode for Full Frame
    # clocking_scheme = "bilevel"

    # 1: // and Serial in REV;
    # 2: // in REV, Serial FWD (representative offset & r.o.n)
    clock_direction = "FWD"

    if num_bias:

        # BOTH sides simultaneously -- OK in TVAC, impossible with actual DPU
        ccd_side = 'BOTH'
        dpu.on_frame_number_do(3, dpu.n_cam_reverse_clocking, num_cycles=num_bias, clock_dir_serial=clock_direction,
                               ccd_order=ccd_order, ccd_side=ccd_side)

    # D. ACQUIRE FULL FRAME DARKS

    if num_dark:

        # # BOTH sides simultaneously -- OK in TVAC, impossible with actual DPU
        ccd_side = 'BOTH'

        #
        #n_cam_partial_ccd(num_cycles=num_dark, row_start=row_start, row_end=row_end, col_end=col_end,
        #                       rows_final_dump=rows_final_dump, ccd_order=ccd_order, ccd_side=ccd_side)

        dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_dark, ccd_side=ccd_side)

    system_to_idle()
