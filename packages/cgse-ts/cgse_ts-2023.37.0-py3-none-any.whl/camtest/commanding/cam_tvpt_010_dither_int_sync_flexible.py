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
    -  TRP1 temperature is set by the operator before executing this one.
        Wait for thermal stabilization
        Perform "quick focus test" while waiting (still to be written)
    - visit all FoV positions -- flexible specification of positions to visit via "thetas, phis"
            visit all 25 sub-pixel random positions
            Acquire 2 images
            Acquire 2 background images

Authors: P. Royer, M. Pertenais

Versions:
    2022 02 10 - 1.0 Creation
"""

import logging

import numpy as np
from random import uniform
import time

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.dpu import wait_cycles
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles
# from egse.system import wait_until

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_010_dither_int_sync_flexible(num_subpix=None, num_frames=None, num_bck=None, thetas=None, phis=None, grid=None, n_rows=None, exposure_time=None, clearout=None, dith_amp=None, fwc_fraction=None, fov_selection=None):
    """
    SYNOPSIS
    cam_tvpt_010_dither_int_sync_flexible(num_subpix=None, num_frames=None, num_bck=None, thetas=None, phis=None, grid=None, n_rows=None, exposure_time=None, clearout=None, dith_amp=None, fwc_fraction=None, fov_selection=None):


    Acquisition for 5 TRP1 temperatures of
        - any set of FoV positions
        - in each FoV position num_subpix sub-pixels positions
        - in each sub-pixel positions a total of num_frames images

    num_subpix    : int, number of ditherings
    num_frames    : int, nb of images acquired at every single dither position
    num_bck       : int, nb of background images acquired at every FoV position, before dithering
    thetas, phis  : elevations and azimuths of the FoV positions to visit
    grid          : False : use [thetas, phis] as a simple list of coordinates. The 2 arrays must have the same size
                    True  : make a 2d grid from the input thetas & phis, i.e. visit every phi for every theta
                            (nested loop with phis outside)

    n_rows        : int, nb of rows to be readout around the expected source position (e.g. 500 = 250 below, 250 above)
    exposure_time : float, effective exposure time. The cycle_time is computed from it
                    (cycle_time = exposure_time + readout_time)
    clearout      : bool, include a clearout after every readout, or not
    dith_amp      : float, amplitude of the random dithering [degrees]
    fwc_fraction  : ogse attenuation (sent to ogse.set_fwc_fraction)
    fov_selection : None, or a list (or numpy array) of field of view

    EXAMPLES
    $ execute(cam_tvpt_010_int_sync,temperature=-80, num_subpix=25,num_frames=2, num_bck=2, exposure_time=2.)
    $ execute(cam_tvpt_010_int_sync,temperature=-75, num_subpix=10,num_frames=2, num_bck=2, exposure_time=4.)

    """
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

    # TEMPERATURE IS AS EXPECTED ?
    # temp = get_housekeeping("tou_rtd_tav")
    #
    # if temp < temperature - 1 or temp > temperature +1:
    #     raise Abort("The temperature at TRP1 is wrong.")
    #
    # if not tcs.temp_stabilized():
    #     raise Abort("Temperature is not stabilized")

    ####################################################
    # OGSE ATTENUATION
    ####################################################

    ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)

    # wait_until(ogse.attenuator_is_ready(), interval=1, timeout=30)


    ####################################################
    # FOV GEOMETRY DEFINITION
    ####################################################

    if grid:
        tmp2d = np.meshgrid(thetas, phis)
        thetas = np.ravel(tmp2d[0])
        phis = np.ravel(tmp2d[1])

    fov_coordinates = angles = np.vstack([thetas, phis]).T


    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles=angles, distorted=True, verbose=True)

    LOGGER.info(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
    c = 0
    for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
        LOGGER.info(
            f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
        c += 1

    ####################################################
    # DEFINITION TEST PARAMETERS
    ####################################################

    # FOV_SELECTION
    if fov_selection is not None:
        LOGGER.info(f"Selected Field Positions:\n {fov_selection}")
        LOGGER.info(f"Selected Field Positions:\n {fov_coordinates[fov_selection]}")
    else:
        fov_selection = np.arange(len(ccdrows))

    npos = len(fov_selection)

    # C. COMMANDING

    # Branching for requested clearout after every readout
    hclearout = {True: 4510, False: 0}

    # for posid, position in enumerate(fov_coordinates):

    c = 0
    for posid, position in zip(fov_selection, fov_coordinates[fov_selection]):
        c+=1

        # Point CAM to first FoV position
        theta0 = position[0]
        phi0 = position[1]

        LOGGER.info(f"pos {posid}  (pos {c:2d}/{npos}). Pointing source to field angles  [{theta0}, {phi0}]")

        point_source_to_fov(theta=theta0, phi=phi0, wait=True)
        visit_field_angles(theta0, phi0)

        # Acquire background images:
        LOGGER.info(f"Acquiring Background frames for the FoV position ({theta0}, {phi0})")

        n_fee_parameters = dict()
        n_fee_parameters["num_cycles"] = num_bck
        n_fee_parameters["row_start"] = max(0, ccdrows[posid]-n_rows//2)
        n_fee_parameters["row_end"] = min(4509, ccdrows[posid]+n_rows//2)
        n_fee_parameters["rows_final_dump"] = hclearout[clearout]
        n_fee_parameters["ccd_order"] = [ccdcodes[posid], ccdcodes[posid], ccdcodes[posid], ccdcodes[posid]]
        n_fee_parameters["ccd_side"] = ccdsides[posid]

        dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)


        # Start infinite loop of acquisition
        LOGGER.info(f"Acquiring Images for the FoV position ({theta0}, {phi0})")
        ogse.shutter_open()

        n_fee_parameters["num_cycles"] = 0
        dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

        for subpix in range(num_subpix-1):
            # num_subpix random positions around these x,y coordinates

            wait_cycles(num_frames)
            theta = theta0 + uniform(-dith_amp, dith_amp)
            phi = phi0 + uniform(-dith_amp, dith_amp)
            dpu.on_long_pulse_do(point_source_to_fov, theta=theta, phi=phi, wait=False)

        wait_cycles(num_frames)     # this for the last (25th) dither position

        # num_cycles = 0 --> explicit commanding of dump_mode_int_sync
        dpu.n_cam_to_dump_mode_int_sync()

        # close shutter and stop acquiring images before moving to next FoV position:
        ogse.shutter_close()

    # Put the setup back to idle, ready for the next test
    system_to_idle()
