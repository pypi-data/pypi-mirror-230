"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

N-CAM

Start condition:
    Shutter closed
    CAM in DUMP mode

End status
    Shutter closed
    CAM in DUMP mode

Synopsis:
    - acquire a single cube of images via dpu.n_cam_partial_ccd
    - image acquisition:
        num_cycles
        external sync
        partial readout / full readout via input parameters

Authors: P. Royer

Versions:
    2021 11 26 - 0.1 Creation
"""
import logging

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle

LOGGER = logging.getLogger(__name__)


@building_block
def cam_single_cube_ext_sync_no_pointing(num_cycles=None, row_start=None, row_end=None, rows_final_dump=None,
                                         ccd_order=None, ccd_side=None, attenuation=None):
    """

    SYNOPSIS
    cam_single_cube_ext_sync_no_pointing(num_cycles=None, row_start=None, row_end=None, rows_final_dump=None,
                                         ccd_order=None, ccd_side=None, attenuation=None)

    INPUTS
    num_cycles    : int, nb of images acquired at every single dither position
    row_start, row_end : specify partial readout parameters. For full frame incl parallel overscan, use [0,4539]
    rows_final_dump : use 0 by default. For clearout after readout, use 4510
    ccd_order : list of 4 numbers in [1,2,3,4]
    ccd_side  : in ["E", "F", "BOTH"]

    attenuation  : fwc_fraction, will be used to command the ogse

    EXAMPLES
    $execute(cam_single_cube_ext_sync_no_pointing, num_cycles=5, row_start=0, row_end=4539, rows_final_dump=0,
             ccd_order=[1,2,3,4], ccd_side="BOTH", attenuation=1.0)

    """
    LOGGER.info("START: cam_single_cube_ext_sync_no_pointing")

    ####################################################
    # STARTING CONDITIONS
    ####################################################

    # ALL SYSTEMS GO ?
    system_test_if_idle()


    ####################################################
    #  OGSE ATTENUATION
    ####################################################

    LOGGER.info(f"Setting OGSE fwc_fraction to {attenuation=}")
    ogse.set_fwc_fraction(fwc_fraction=attenuation)

    ####################################################
    #  IMAGE ACQUISITION
    ####################################################

    # Acquire background images:
    LOGGER.info(f"Acquiring {num_cycles} images")

    ogse.shutter_open()

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["row_start"] = row_start
    n_fee_parameters["row_end"] = row_end
    n_fee_parameters["rows_final_dump"] = rows_final_dump
    n_fee_parameters["ccd_order"] = ccd_order
    n_fee_parameters["ccd_side"] = ccd_side

    # Issue command at 3rd short pulse -> takes effect at the next long pulse
    dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, **n_fee_parameters)

    ogse.shutter_close()

    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_single_cube_ext_sync_no_pointing")
