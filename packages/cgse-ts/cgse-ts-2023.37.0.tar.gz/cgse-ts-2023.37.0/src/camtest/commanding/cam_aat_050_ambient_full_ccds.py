"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

Goal : obtain full frame images of a list of CCDs at ambient

Application : source identification / debugging the CCD order & CCD sides new implementation at FEE level

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    CAM in DUMP mode
    OGSE attenuation set [to get a decent signal i.e. min a few thousand a.d.u. with the exposure_time commanded here]

End status
    Shutter closed
    CAM in DUMP mode

Synopsis:
    - go to the selected position in the FoV
    - acquire a full-frame image on a CCD
    - repeat the acquisition for all CCDs in the input list of CCDs to be covered
    - image acquisition:
        n_cycles
        full frame
        BOTH sides
        internal sync, with "exposure_time"

Authors: P. Royer

Versions:
    2022 12 12 - 0.1 Creation
"""
import logging

import time

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)

@building_block
def cam_ambient_full_ccds(theta=None, phi=None, num_cycles=None, exposure_time=None, ccds=None, ccd_side=None, attenuation=None):
    """

    SYNOPSIS
    cam_ambient_full_ccds(theta=None, phi=None, num_cycles=None, exposure_time=None, ccds=None, ccd_side=None, attenuation=None)

    INPUTS
    theta,phi     : FoV location, i.e. [boresight_angle, azimuth], in degrees
    num_cycles    : int, nb of images acquired at every single dither position
    exposure_time : float, effective exposure time. The cycle_time is computed from it
                    (cycle_time = exposure_time + readout_time)
    ccds          : [int] list of ccd numbers to be covered in the observation, e.g. [1,2,3,4]
    ccd_side      : in ['E', 'F', 'BOTH']
    attenuation   : fwc_fraction, will be used to command the ogse

    EXAMPLES
    $ execute(cam_ambient_full_ccds, theta=8.3, phi=-9, num_cycles=5, exposure_time=1.,
    ccds=[1,2,3,4], ccd_side='BOTH', attenuation=1.)

    """
    LOGGER.info("START: cam_ambient_full_ccds")

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

    while dpu.n_cam_is_ext_sync():
        time.sleep(1.)

    ####################################################
    #  OGSE ATTENUATION
    ####################################################

    LOGGER.info(f"Setting OGSE fwc_fraction to {attenuation=}")
    ogse.set_fwc_fraction(fwc_fraction=attenuation)


    ####################################################
    #  POINTING
    ####################################################

    if (theta is None) or (phi is None):
        LOGGER.info(f"No pointed requested: input field angles ({theta}, {phi})")
    else:
        LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
        point_source_to_fov(theta=theta, phi=phi, wait=True)
        visit_field_angles(theta, phi)

    ####################################################
    #  IMAGE ACQUISITION
    ####################################################

    LOGGER.info(f"Image acquisition")

    ogse.shutter_open()

    n_fee_parameters = dict()
    n_fee_parameters["num_cycles"] = num_cycles
    n_fee_parameters["row_start"] = 0
    n_fee_parameters["row_end"] = 4509
    n_fee_parameters["rows_final_dump"] = 4510
    n_fee_parameters["ccd_side"] = ccd_side
    n_fee_parameters["exposure_time"] = exposure_time

    for ccd in ccds:

        n_fee_parameters["ccd_order"] = [ccd, ccd, ccd, ccd]

        dpu.n_cam_partial_int_sync(**n_fee_parameters)

    ogse.shutter_close()

    ####################################################
    #  RESET TO STANDARD CONDITIONS
    ####################################################

    # Put the setup back to idle, ready for the next test
    LOGGER.info("System to idle")
    system_to_idle()

    # Put the setup back to idle, ready for the next test
    LOGGER.info("END: cam_ambient_full_ccds")
