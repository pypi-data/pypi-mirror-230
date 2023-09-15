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
        - visit all FoV positions
            visit all 25 sub-pixel random positions
            Acquire 2 images
            Acquire 2 background images

Authors: M. Pertenais, P. Royer

Versions:
    2020 10 26 - 0.1 Creation
    2022 02 10 - 0.2 N. Gorius: Added flexibility on the number of positions visited using 'fov_table' as keyword for loading information in the setup.
                     Editorial changes in the synopis.
    2023 02 27 - 1.0 P.R. Merge the standard and _IAS version (add. parameter 'bandpass').
    2023 06 27 - 1.1 N. Gorius: Following PFM TVAC test as IAS, additional checks using dpu.n_cam_is_dump_mode() are introduced.

"""
import logging

import numpy as np
from random import uniform
import time

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.dpu import wait_cycles
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from camtest.commanding.mgse import point_source_to_fov
from egse.exceptions import Abort
from egse.visitedpositions import visit_field_angles
# from egse.system import wait_until

from egse.state import GlobalState

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_010_int_sync(num_subpix=None, num_frames=None, num_bck=None, n_rows=None, exposure_time=None, clearout=None, dith_amp=None, fwc_fraction=None, fov_table=None, fov_selection=None, bandpass=None):
    """
    SYNOPSIS
    cam_tvpt_010_int_sync(num_subpix=None, num_frames=None, num_bck=None, n_rows=None, exposure_time=None, clearout=None, dith_amp=None, fwc_fraction=None, fov_table=None, fov_selection=None, bandpass=1)

    Work-horse for typical use during TVAC test:
    Acquisition for 5 TRP1 temperatures of
        - 40 FoV positions
        - in each FoV position num_subpix sub-pixels positions
        - in each sub-pixel positions a total of num_frames images


    num_subpix    : int, number of ditherings
    num_frames    : int, nb of images acquired at every single dither position
    num_bck       : int, nb of background images acquired at every FoV position, before dithering
    n_rows        : int, nb of rows to be readout around the expected source position (e.g. 500 = 250 below, 250 above)
    exposure_time : float, effective exposure time. The cycle_time is computed from it
                    (cycle_time = exposure_time + readout_time)
    clearout      : bool, include a clearout after every readout, or not
    dith_amp      : float, amplitude of the random dithering [degrees]
    fwc_fraction  : ogse attenuation (sent to ogse.set_fwc_fraction)
    fov_table     : provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')
    fov_selection : None, or a list (or numpy array) of field of view

    bandpass: IAS: Index in filter wheel 1 of the bandpass filter that is requested (1: Green, 2: Red, 3: NIR).
              SRON, INTA : NotImplemented

    EXAMPLES
    $ execute(cam_tvpt_010_int_sync, num_subpix=25, num_frames=4, num_bck=2, n_rows=250, exposure_time=0.2, clearout=True, dith_amp=0.012, fwc_fraction=0.00005, fov_selection=[1,5,20], fov_table="reference_full_40", description="Transient monitoring PSF across FoV to -90C", bandpass=2)

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

    if bandpass is None:
        ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)
    else:
        ogse.set_fwc_fraction_bandpass(fwc_fraction=fwc_fraction, bandpass=bandpass)

    # wait_until(ogse.attenuator_is_ready(), interval=1, timeout=30)

    ####################################################
    # DEFINITION TEST PARAMETERS
    ####################################################
    if fov_table is None:
        raise Abort(f"Argument 'fov_table' is None and should be defined.")

    setup = GlobalState.setup
    try:
        tab = setup.fov_positions[fov_table]
    except:
        raise Abort(f"The requested FoV table {fov_table} is not defined in the current setup")

    if len(tab['theta']) == 0 or len(tab['theta']) != len(tab['phi']):
        raise Abort(f"The requested FoV table {fov_table} has an invalid format. Theta:{len(tab['theta'])}, Phi:{len(tab['phi'])}")

    use_angles = True
    verbose    = True

    ccdrows, ccdcols, ccdcodes, ccdsides, fov_coordinates = fov_geometry_from_table(distorted=True,
                                distorted_input=False, table_name=fov_table, use_angles=use_angles, verbose=verbose)

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

        if ccdrows[posid] is None or ccdcols[posid] is None or ccdcodes[posid] is None or ccdsides[posid] is None:
            LOGGER.warning(f"Invalid Selected Field Positions:\n {fov_coordinates[fov_selection]}")
            continue

        # Point CAM to first FoV position
        theta0 = position[0]
        phi0 = position[1]

        LOGGER.info(f"pos {posid}  (pos {c:2d}/{npos}). Pointing source to field angles  [{theta0}, {phi0}]")

        point_source_to_fov(theta=theta0, phi=phi0, wait=True)
        visit_field_angles(theta0, phi0)

        # Acquire background images:
        if num_bck != 0:
            while not dpu.n_cam_is_dump_mode():
                time.sleep(1.0)
            
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
        while not dpu.n_cam_is_dump_mode():
            time.sleep(1.0)
        
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
