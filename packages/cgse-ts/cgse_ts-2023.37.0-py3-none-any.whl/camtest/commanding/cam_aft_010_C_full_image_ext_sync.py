"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT:
PLATO ANALOGUE FUNCTIONAL TEST
    CAM-AFT-010 - PART C
    FEE FULL IMAGE MODE
    EXTERNAL SYNCHRONISATION


N-CAM

Start condition:
    CAM in DUMP mode

End status
    CAM in DUMP mode

Synopsis:

    FEE:
        Full Image
        External Synchronisation

    The test mostly relies on, and explores the parameter space of dpu.n_cam_partial_ccd:

    - partial readout bottom and top of the CCD
    - data acquisition with and without parallel overscan
    - all CCDs : 1 at a time and rotating over CCDs in diff. orders
    - E, F and BOTH CCD sides
    - finite and infinite loop on image acquisition
    - final clearout is requested only with partial readout.
    - reverse_clocking with serial direction FWD and REV


Author: P. Royer

Versions:
    2020 10 29 - 0.1 Creation
"""
import logging

import time

from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle
from camtest.commanding.dpu import wait_cycles

LOGGER = logging.getLogger(__name__)


def cam_aft_010_C_full_image_ext_sync(num_cycles=None, sleep_time=None):
    """
    PLATO analogue functional test
    FEE:
        Full Image
        External Synchronisation

    The test mostly relies on, and explores the parameter space of dpu.n_cam_partial_ccd:

    - partial readout bottom and top of the CCD
    - data acquisition with and without parallel overscan
    - all CCDs : 1 at a time and rotating over CCDs in diff. orders
    - E, F and BOTH CCD sides
    - finite and infinite loop on image acquisition
    - final clearout is requested only with partial readout.
    - reverse_clocking with serial direction FWD and REV

    num_cycles : nb of images acquired with each mode.
                 In the infinite loop, this number is doubled

    sleep_time : inserted between the various image acquisition modes

    Test Duration :
        - 16 setups

        - cycle_time = 25 seconds

        - 10 sec wait times between the tests (sleep_time) -> 70 seconds

        -> with num_cycles = 5:
        Duration ~ (5 * 25 * 16) + 70 ~ 35 minutes

    """

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    #############################
    # PARAMETER SPACE EXPLORATION
    #############################

    LOGGER.info("n_cam_partial_ccd: CCD1E rows [0,500]")

    n_fee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=500,
        rows_final_dump=0,
        ccd_order=[1, 1, 1, 1],
        ccd_side='E',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **n_fee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD1F rows [4000,4509]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=4000,
        row_end=4509,
        rows_final_dump=4510,
        ccd_order=[1, 1, 1, 1],
        ccd_side='F',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD2E rows [4000,4539] - Parallel Overscan")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=4000,
        row_end=4539,
        rows_final_dump=4510,
        ccd_order=[2, 2, 2, 2],
        ccd_side='E',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD2 F - FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4509,
        rows_final_dump=0,
        ccd_order=[2, 2, 2, 2],
        ccd_side='F',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD3 E - FULL - Parallel Overscan")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4539,
        rows_final_dump=0,
        ccd_order=[3, 3, 3, 3],
        ccd_side='E',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD3 BOTH rows [1000,2000]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=1000,
        row_end=2000,
        rows_final_dump=4510,
        ccd_order=[3, 3, 3, 3],
        ccd_side='BOTH',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD4 BOTH FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4539,
        rows_final_dump=0,
        ccd_order=[4, 4, 4, 4],
        ccd_side='BOTH',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: CCD4E rows [1500, 2500] Infinite Loop & wait_cycles")

    nfee_parameters = dict(
        num_cycles=0,
        row_start=1500,
        row_end=2500,
        rows_final_dump=4510,
        ccd_order=[4, 4, 4, 4],
        ccd_side='E',
    )

    # Launch the infinite loop
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    # Wait for image acquisition (this exits at frame number 3)
    wait_cycles(num_cycles)

    # Interrupt the infinite loop
    dpu.n_cam_to_dump_mode()

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: ALL CCDs F-side - rows [1000,2000]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=1000,
        row_end=2000,
        rows_final_dump=4510,
        ccd_order=[1, 2, 3, 4],
        ccd_side='F',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: ALL CCDs alt. order. E-side - rows [1000,2000]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=1000,
        row_end=2000,
        rows_final_dump=4510,
        ccd_order=[3, 1, 4, 2],
        ccd_side='E',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_partial_ccd: ALL CCDs alt. order. E-side - FULL - Parallel Overscan")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4539,
        rows_final_dump=0,
        ccd_order=[4, 3, 2, 1],
        ccd_side='E',
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_full_ccd: Repeat Prev: ALL CCDs alt. order. E-side - FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        ccd_order=[4, 3, 2, 1],
        ccd_side='E',
        rows_overscan=30
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_full_ccd: ALL CCDs BOTH - FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        ccd_order=[1, 2, 3, 4],
        ccd_side='BOTH',
        rows_overscan=30
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_full_standard: ALL CCDs BOTH - FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        ccd_side='BOTH'
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_full_standard, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_reverse_clocking: ALL CCDs BOTH - SERIAL FWD")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        clock_dir_serial="FWD",
        ccd_order=[1, 2, 3, 4],
        ccd_side='BOTH'
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_reverse_clocking, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_reverse_clocking: ALL CCDs BOTH - SERIAL REV")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        clock_dir_serial="REV",
        ccd_order=[1, 2, 3, 4],
        ccd_side='BOTH'
    )
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_reverse_clocking, **nfee_parameters)

    # TODO :
    #  REMOVE PARTIAL READOUT PARAMETERS
    #  ACTIVATE AFTER THE MODE IS FIXED.
    #
    # time.sleep(sleep_time)
    #
    # LOGGER.info("n_cam_charge_injection: ALL CCDs")
    # nfee_parameters = dict(
    #     num_cycles=num_cycles,
    #     row_start=0,
    #     row_end=4539,
    #     rows_final_dump=0,
    #     ccd_order=[1, 2, 3, 4],
    #     ccd_side='BOTH',
    #     ci_width=100,
    #     ci_gap=200)
    # dpu.n_cam_reverse_clocking(**nfee_parameters)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
