"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT:
PLATO ANALOGUE FUNCTIONAL TEST
    CAM-AFT-010 - PART B
    FEE FULL IMAGE MODE
    INTERNAL SYNCHRONISATION


N-CAM

Start condition:
    CAM in DUMP mode or DUMP mode int sync

End status
    CAM in DUMP mode

Synopsis:

    FEE:
        Full Image
        Internal Synchronisation

    The test relies on, and explores the parameter space of dpu.n_cam_partial_int_sync:

    - partial readout bottom and top of the CCD
    - data acquisition with and without parallel overscan
    - all CCDs (1 at a time; rotating over CCDs is not possible with FEE internal sync)
    - E, F and BOTH CCD sides
    - finite and infinite loop on image acquisition
    - final clearout is always requested

Author: P. Royer

Versions:
    2020 10 29 - 0.1 Creation
"""
import logging

import time

from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle
from camtest.commanding.dpu import wait_cycles
from egse.exceptions import Abort

LOGGER = logging.getLogger(__name__)


def cam_aft_010_B_full_image_int_sync(num_cycles=None, exposure_time=None, sleep_time=None):
    """
    PLATO analogue functional test
    FEE:
        Full Image
        Internal Synchronisation

    The test relies on, and explores the parameter space of dpu.n_cam_partial_int_sync:

    - partial readout bottom and top of the CCD
    - data acquisition with and without parallel overscan
    - all CCDs (1 at a time; rotating over CCDs is not possible with FEE internal sync)
    - E, F and BOTH CCD sides
    - finite and infinite loop on image acquisition
    - final clearout is always requested

    num_cycles : nb of images acquired with each mode.
                 In the infinite loop, this number is doubled

    exposure_time : exposure time used for the image acquisition in every mode
                    Given the ambient conditions, and the fact that we're not aiming at
                    observing a real source, it should be kept very short (e.g. 0.25 sec).

    sleep_time : inserted between the various image acquisition modes

    Test Duration :
        - 8 setups =
            5 with partial readout (incl. inf. loop)
            cycle_time ~~ (exposure_time + 1 (readout) + 0.5 (clearout)) ~ 2 sec

            3 with full frame readout
            cycle_time ~~ (exposure_time + 4 (readout) + 0.5 (clearout)) ~ 5 sec

        - 10 sec wait times between the tests (sleep_time) -> 70 seconds

        - 30 seconds to secure dump_mode_int_sync at the start

        - with exposure_time < -0.5 sec and num_cycles = 5 :

        Duration ~ (5 * 2 * 6) + (5 * 5 * 3) + 70 + 30 < 5 minutes

    """

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()



    #########################
    # DUMP MODE INTERNAL SYNC
    #########################
    LOGGER.info("DUMP MODE Internal Sync")

    dpu.n_cam_to_dump_mode_int_sync()

    time.sleep(30)
    if not dpu.n_cam_is_dump_mode():
        raise Abort("Putting the N-FEE in dump mode did not succeed")

    # Wait time for the operator to check we're in DUMP mode internal sync
    # time.sleep(60)

    #############################
    # PARAMETER SPACE EXPLORATION
    #############################

    LOGGER.info("CCD1E rows [0,500]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=500,
        rows_final_dump=4510,
        ccd_order=[1, 1, 1, 1],
        ccd_side='E',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD1F rows [4000,4509]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=4000,
        row_end=4509,
        rows_final_dump=4510,
        ccd_order=[1, 1, 1, 1],
        ccd_side='F',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD2E rows [4000,4539] - Parallel Overscan")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=4000,
        row_end=4539,
        rows_final_dump=4510,
        ccd_order=[2, 2, 2, 2],
        ccd_side='E',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD2 F - FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4509,
        rows_final_dump=4510,
        ccd_order=[2, 2, 2, 2],
        ccd_side='F',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD3 E - FULL - Parallel Overscan")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4539,
        rows_final_dump=4510,
        ccd_order=[3, 3, 3, 3],
        ccd_side='E',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD3 BOTH rows [1000,2000]")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=1000,
        row_end=2000,
        rows_final_dump=4510,
        ccd_order=[3, 3, 3, 3],
        ccd_side='BOTH',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD4 BOTH FULL")
    nfee_parameters = dict(
        num_cycles=num_cycles,
        row_start=0,
        row_end=4539,
        rows_final_dump=4510,
        ccd_order=[4, 4, 4, 4],
        ccd_side='BOTH',
        exposure_time=exposure_time
    )
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("CCD4E rows [1500, 2500] Infinite Loop & wait_cycles (2 x num_cycles)")

    nfee_parameters = dict(
        num_cycles=0,
        row_start=1500,
        row_end=2500,
        rows_final_dump=4510,
        ccd_order=[4, 4, 4, 4],
        ccd_side='E',
        exposure_time=exposure_time
    )

    # Launch the infinite loop
    dpu.n_cam_partial_int_sync(**nfee_parameters)

    # Wait for image acquisition
    wait_cycles(num_cycles * 2.)

    # Interrupt the infinite loop
    dpu.n_cam_to_dump_mode_int_sync()


    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning to DUMP MODE")

    dpu.n_cam_to_dump_mode()

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
