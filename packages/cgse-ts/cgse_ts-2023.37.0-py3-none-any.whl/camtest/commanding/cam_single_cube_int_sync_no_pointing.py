"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.1 CAM-TVPT-010 Camera best focus determination

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Shutter closed
    CAM in DUMP mode
    OGSE attenuation set [to get a decent signal i.e. min a few thousand a.d.u. with the exposure_time commanded here]

End status
    Shutter closed
    CAM in DUMP mode

Synopsis:
    - go to the selected position in the FoV
    - acquire a single cube of images at that location
    - image acquisition:
        n_cycles
        partial readout of 'n_rows'
        internal sync, with "exposure_time"

Authors: P. Royer

Versions:
    2021 11 12 - 0.1 Creation
"""
import logging

import time
from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle

LOGGER = logging.getLogger(__name__)


@building_block
def cam_single_cube_int_sync_no_pointing(num_cycles=None, row_start=None, row_end=None, rows_final_dump=None,
                             ccd_order=None, ccd_side=None, exposure_time=None, attenuation=None):
    """

    SYNOPSIS
    cam_single_cube_int_sync_no_pointing(num_cycles=None, row_start=None, row_end=None, rows_final_dump=None,
                             ccd_order=None, ccd_side=None, exposure_time=None, attenuation=None)

    INPUTS
    num_cycles    : int, nb of images acquired at every single dither position
    row_start, row_end : specify partial readout parameters. For full frame incl parallel overscan, use [0,4539]
    rows_final_dump : use 0 by default. For clearout after readout, use 4510
    ccd_order : list of 4 numbers in [1,2,3,4]
    ccd_side  : in ["E", "F", "BOTH"]
    exposure_time : float, effective exposure time. The cycle_time is computed from it
                    (cycle_time = exposure_time + readout_time)
    attenauation  : fwc_fraction, will be used to command the ogse

    EXAMPLES
    $ execute(cam_single_cube_int_sync(num_cycles=5, row_start=0, row_end=4509, rows_final_dump=4510,
                             ccd_order=[1,1,1,1], ccd_side='E', exposure_time=1., attenuation=1.0)

    """
    LOGGER.info("START: cam_single_cube_int_sync_no_pointing")

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()

    # SET THE CAMERA IN DUMP MODE INTERNAL SYNC
    # Preparation for FEE-internal sync data acquisition
    dpu.n_cam_to_dump_mode_int_sync()

    ####################################################
    #  FEE READY ?
    ####################################################

    while (dpu.n_cam_is_ext_sync()):
        time.sleep(1.)

    ####################################################
    #  OGSE ATTENUATION
    ####################################################

    LOGGER.info(f"Setting OGSE fwc_fraction to {attenuation=}")
    ogse.set_fwc_fraction(fwc_fraction=attenuation)

    ####################################################
    #  IMAGE ACQUISITION
    ####################################################

    # Acquire images:
    LOGGER.info(f"Acquiring Images")

    ogse.shutter_open()

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["row_start"] = row_start
    n_fee_parameters["row_end"] = row_end
    n_fee_parameters["rows_final_dump"] = rows_final_dump
    n_fee_parameters["ccd_order"] = ccd_order
    n_fee_parameters["ccd_side"] = ccd_side
    n_fee_parameters["exposure_time"] = exposure_time

    dpu.n_cam_partial_int_sync(**n_fee_parameters)

    ogse.shutter_close()

    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_single_cube_int_sync_no_pointing")
