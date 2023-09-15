"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.4 CAM-TVPT-045 CCD characterization

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in STANDBY

End status
    NFEE in STANDBY

Synopsis:
    - FEE to reverse clocking
        Acquire 100 "bias" frames
    - FEE to full image mode
        Acquire 3 full images (integration time of 900 seconds)

Authors: C. Paproth

Versions:
    2021 05 04 - 0.1 Draft -- Creation (based on cam_tvlpt_030_test_673_dark_ncam.py written by P. Royer and R. Huygen)
    2021 06 22 - 0.2 Implement 900 sec integration time
    2021 10 08 - 0.3 Update after meeting on 08.10.2021
    2021 11 12 - 0.4 Change number of overscan rows
    2023 04 04 - 0.5 Use dump gate high instead of reverse clocking
    2023 07 20 - 0.6 NG - Split acquisition of bias frames between E and F side (see git issue#1184)

"""
                  
from camtest.commanding import system_test_if_idle, system_to_idle, dpu
from camtest.commanding.dpu import n_cam_reverse_clocking, n_cam_full_ccd, wait_cycles
from camtest.core.exec import building_block


@building_block
def cam_tvpt_045(num_bias = None, num_dark = None, int_time = None):
    """
    SYNOPSIS
    cam_tvpt_045(num_bias = 100, num_dark = 3, int_time = 900)

    1. Acquisition of 'num_bias' full frames, CCDs in reverse clocking
            Reverse clocking scheme : parallel in REV, serial in FWD
            --> provides representative electronic offset and r.o.n.

    2. Acquisition of 'num_dark' full frames with 'int_time' seconds integration time

    EXAMPLE
    $ execute(cam_tvlpt_045, num_bias = 100, num_dark = 3, int_time = 900)

    """
    # A. CHECK STARTING CONDITIONS
    system_test_if_idle()

    # Generic Parameters for full frame acquisition over all CCDs
    row_start = 0
    row_end = 4540
    #col_end = 2295  # Default = 2295; includes serial pre- & overscans
    ccd_order = [1, 2, 3, 4]

    # C. ACQUIRE REFERENCE FULL FRAME "BIAS" FRAMES

    if num_bias:

        # E and F sides separately
        ccd_side = 'E'
        dpu.on_frame_number_do(3, dpu.n_cam_acquire_and_dump, num_cycles=num_bias, row_start=0, row_end=4539, rows_final_dump=0,
                               ccd_order=ccd_order, ccd_side=ccd_side)
        ccd_side = 'F'
        dpu.on_frame_number_do(3, dpu.n_cam_acquire_and_dump, num_cycles=num_bias, row_start=0, row_end=4539, rows_final_dump=0,
                               ccd_order=ccd_order, ccd_side=ccd_side)

    # D. ACQUIRE FULL FRAME DARKS

    # Parameters for full frame acquisition over all CCDs
    rows_final_dump = 4510  # Full frame clearout after every readout
    rows_overscan = 1000

    # # BOTH sides simultaneously -- OK in TVAC, impossible with actual DPU
    ccd_side = 'BOTH'
    num_cycles = int(int_time / 25)

    for i in range(num_dark):
        ccd_order = [3, 4, 3, 4]
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=ccd_order, ccd_side='E', rows_overscan=30)
        wait_cycles(num_cycles)
        ccd_order = [1, 2, 3, 4]
        dpu.n_cam_full_ccd(num_cycles=1, ccd_order=ccd_order, ccd_side='E', rows_overscan=rows_overscan)

        ccd_order = [3, 4, 3, 4]
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=ccd_order, ccd_side='F', rows_overscan=30)
        wait_cycles(num_cycles)
        ccd_order = [1, 2, 3, 4]
        dpu.n_cam_full_ccd(num_cycles=1, ccd_order=ccd_order, ccd_side='F', rows_overscan=rows_overscan)

        ccd_order = [1, 2, 1, 2]
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=ccd_order, ccd_side='E', rows_overscan=30)
        wait_cycles(num_cycles)
        ccd_order = [1, 2, 3, 4]
        dpu.n_cam_full_ccd(num_cycles=1, ccd_order=ccd_order, ccd_side='E', rows_overscan=rows_overscan)

        ccd_order = [1, 2, 1, 2]
        dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=ccd_order, ccd_side='F', rows_overscan=30)
        wait_cycles(num_cycles)
        ccd_order = [1, 2, 3, 4]
        dpu.n_cam_full_ccd(num_cycles=1, ccd_order=ccd_order, ccd_side='F', rows_overscan=rows_overscan)

    system_to_idle()
    

