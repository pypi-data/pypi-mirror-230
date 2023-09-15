"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.4.1 CAM-ALPT-030 short dark current measurement at ambient temperature

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Test environment in IDLE state (FEE in dump mode)

End status
    Test environment in IDLE state

Synopsis:
    - FEE to reverse clocking
        Acquire 10 "bias" frames
    - FEE to full image mode
        Acquire 10 full images

Comments:
    - The expected dark current is ~ 50000 e- / second, which explains
      the necessity for short cycle times, hence the FEE internal sync

Author: P.Royer

Versions:
    2021 10 29 - Creation from the operational-temperature version

"""
import logging

import time

from camtest.commanding import dpu
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.core.exec import building_block
from egse.exceptions import Abort

LOGGER = logging.getLogger(__name__)


@building_block
def cam_alpt_030(num_bias=None, num_dark=None, exposure_times=None):
    """
    SYNOPSIS
    cam_tvlpt_030(num_bias=None,num_dark=None)


    1. Acquisition of 'num_bias' full frames, CCDs in reverse clocking
            Reverse clocking scheme : parallel in REV, serial in FWD
            --> provides representative electronic offset and r.o.n.

    2. Acquisition of 'num_dark'
            FEE internal synchronisation
            Every CCD in turn
            Different exposure times, as specified in 'exposure_times'

    CCDs are read in full frame -> cycle_time = exposure_time + 4

    Duration :
        num_bias * 25 +
        4 (ccds) * [num_dark * (sum(exposure_times) + 4 (sec/readout) * len(exposure_times))]

        num_bias = num_dark = 10
        exposure_times = [1,5,10]
        --> Duration ~ 250 + 4 * 280 < 30 min

    EXAMPLE
    $ execute(cam_tvlpt_030,num_bias=100,num_dark=100,exposure_times=[1, 5, 10])

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

        LOGGER.info("BIAS")

        # BOTH sides simultaneously -- OK in TVAC, impossible with actual DPU
        ccd_side = 'BOTH'
        dpu.on_frame_number_do(3, dpu.n_cam_reverse_clocking, num_cycles=num_bias, clock_dir_serial=clock_direction,
                               ccd_order=ccd_order, ccd_side=ccd_side)

    # D. ACQUIRE FULL FRAME DARKS

    if num_dark:

        # STANDARD OBS MODE, INAPPROPRIATE AT AMBIENT
        # # # BOTH sides simultaneously -- OK in TVAC, impossible with actual DPU
        # ccd_side = 'BOTH'
        #
        # #
        # #n_cam_partial_ccd(num_cycles=num_dark, row_start=row_start, row_end=row_end, col_end=col_end,
        # #                       rows_final_dump=rows_final_dump, ccd_order=ccd_order, ccd_side=ccd_side)
        #
        # n_cam_full_standard(num_cycles=num_dark, ccd_side=ccd_side)

        # FEE INTERNAL SYNC

        LOGGER.info("DUMP MODE Internal Sync")

        dpu.on_frame_number_do(3, dpu.n_cam_to_dump_mode_int_sync)

        time.sleep(30)

        if not dpu.n_cam_is_dump_mode():
            raise Abort("Putting the N-FEE in dump mode did not succeed")

        LOGGER.info("DARK")

        nfee_parameters = dict(
            num_cycles=num_dark,
            row_start=0,
            row_end=4539,
            rows_final_dump=4510,
            ccd_side='BOTH',
        )

        for ccd in [1, 2, 3, 4]:

            LOGGER.info(f"DARK - {ccd=}")

            nfee_parameters['ccd_order'] = [ccd, ccd, ccd, ccd]

            for exposure_time in exposure_times:

                nfee_parameters['exposure_time'] = exposure_time

                dpu.n_cam_partial_int_sync(**nfee_parameters)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
