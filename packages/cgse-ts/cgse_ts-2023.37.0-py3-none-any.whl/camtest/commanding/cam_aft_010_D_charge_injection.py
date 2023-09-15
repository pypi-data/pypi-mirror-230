"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT:
PLATO ANALOGUE FUNCTIONAL TEST
    CAM-AFT-010 - PART D
    CHARGE INJECTION

N-CAM

Start condition:
    CAM in DUMP mode

End status
    CAM in DUMP mode

Synopsis:

    FEE:
        Full Image
        External Synchronisation

    The test is focussed on the charge injection

Author: P. Royer, R. Huygen

Versions:
    2020 11 23 - 0.1 Creation (as excerpt from test _aft_010_C)
"""
import logging

import time

from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle

LOGGER = logging.getLogger(__name__)


def cam_aft_010_D_charge_injection(num_cycles=None, sleep_time=None):
    """
    PLATO analogue functional test
    FEE:
        Full Image
        External Synchronisation

    The test focusses on the CCD charge injection.

    num_cycles : nb of images acquired with each mode.
                 In the infinite loop, this number is doubled

    sleep_time : inserted between the various image acquisition modes

    Test Duration :
        - 4 setups

        - cycle_time = 25 seconds

        - 10 sec wait times between the tests (sleep_time) -> 30 seconds

        -> with num_cycles = 5:
        Duration ~ (5 * 25 * 4) + 30 ~ 10 minutes

    """

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    #############################
    # PARAMETER SPACE EXPLORATION
    #############################

    #  ACTIVATE AFTER THE MODE IS FIXED.

    time.sleep(sleep_time)

    LOGGER.info("n_cam_charge_injection: one CCD ci width/gap/vgd: 100/200/17 (30% FWC)")
    nfee_parameters = dict(
         num_cycles=num_cycles,
         row_start=0,
         row_end=4539,
         rows_final_dump=0,
         ccd_order=[2, 2, 2, 2],
         ccd_side='BOTH',
         ci_width=100,
         ci_gap=200,
         vgd=17)
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_charge_injection_full, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_charge_injection: ALL CCDs ci width/gap/vgd: 100/200/16 (50% FWC)")
    nfee_parameters = dict(
         num_cycles=num_cycles,
         row_start=0,
         row_end=4539,
         rows_final_dump=0,
         ccd_order=[1, 2, 3, 4],
         ccd_side='BOTH',
         ci_width=100,
         ci_gap=200,
         vgd=16)
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_charge_injection_full, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_charge_injection: ALL CCDs Full Flood, vgd=15 (70% FWC")
    nfee_parameters = dict(
         num_cycles=num_cycles,
         row_start=0,
         row_end=4539,
         rows_final_dump=0,
         ccd_order=[1, 2, 3, 4],
         ccd_side='BOTH',
         ci_width=4509,
         ci_gap=0,
         vgd=15)
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_charge_injection_full, **nfee_parameters)

    time.sleep(sleep_time)

    LOGGER.info("n_cam_charge_injection: ALL CCDs CTI corr. mode: ci width/gap/vgd 1/4508/14 (FWC)")
    nfee_parameters = dict(
         num_cycles=num_cycles,
         row_start=0,
         row_end=4539,
         rows_final_dump=0,
         ccd_order=[1, 2, 3, 4],
         ccd_side='BOTH',
         ci_width=4509,
         ci_gap=0,
         vgd=14)
    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_charge_injection_full, **nfee_parameters)

    time.sleep(sleep_time)

    ####################################################
    # RESET TO STANDARD CONDITIONS
    ####################################################

    LOGGER.info("End of the procedure -> Returning system to idle.")

    system_to_idle()
