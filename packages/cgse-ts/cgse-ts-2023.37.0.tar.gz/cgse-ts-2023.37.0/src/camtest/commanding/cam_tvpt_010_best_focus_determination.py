"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.1 CAM-TVPT-010 Camera best focus determination

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Shutter closed
    CAM in DUMP mode

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

Authors: M. Pertenais

Versions:
    2020 09 04 - 0.1 Draft -- Creation
    2020 09 08 - 0.2 Draft -- Correction after iteration with Rik
    2021 03 23 - 0.3 Draft -- Addition of background and new acquisition mode
    2021 06 01 - 0.4 Draft -- Preparation of the test rehearsal for the EM at SRON
    2021 09 28 - 0.5 Draft -- Updated version after the test rehearsal and the meeting on 28.09.2021
    2021 10 27 - 0.6 Draft -- Modification of input parameters, addition of the standard FoV calib tables, change to "partial" or "full" modes
    2021 11 03 - 0.7 Draft -- Final Draft provided for the EM test at SRON. Can be changed to 1.0 if required
    2021 12 01 - 0.7 Draft -- Introduce possibility to select the FoV locations to visit in the complete list of 40
    2023 02 27 - 1.0 -- Merge the standard and _IAS version (add. parameter 'bandpass')
    2023 05 02 - 1.1 -- N. Gorius: Replaced 'fov' parameters [hard-coded keyword to specific table] with 'fov_table' parameters similar
                        to cam_tvpt_010_best_focus_determination_int_sync.py. Aligned handling of fov positions using
                        fov_test_geometry.fov_geometry_from_table() similar to the same script.
    2023 06 23 - 1.2 -- N. Gorius: Expanded meaning of 'mode' parameters. Previously it was either 'partial' or 'full'.
                        Now it allows 'full_E_or_F' to record one side based on the source location while cycling through the 4 CCDs.
"""
import logging
from random import uniform

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.dpu import wait_cycles
from camtest.commanding.functions import fov_test_geometry
from camtest.commanding.mgse import point_source_to_fov
from egse.exceptions import Abort
from egse.state import GlobalState
from egse.visitedpositions import visit_field_angles
import numpy as np

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_010(num_subpix=None, num_frames=None, num_bck=None, n_rows=None, mode=None, dith_amp=None, fwc_fraction=None, fov_table=None, fov_selection=None, bandpass=None):
    """
    SYNOPSIS
    cam_tvpt_010(num_subpix=25, num_frames=2, num_bck=2, n_rows=500, mode="partial", dith_amp=0.012, fwc_fraction=1.6, fov_table="reference_full_40", fov_selection=None, bandpass=1)

    Acquisition for a given TRP1 temperature of
        - 40 FoV positions
        - in each FoV position num_subpix sub-pixels positions
        - in each sub-pixel positions a total of num_frames images

    With mode = "partial", the code using partial readout of a single CCD is used
    With mode = "full", the code using the standard CCDs reading sequence
    With mode = "full_E_or_F", the code using the standard CCDs reading sequence BUT only record the side corresponding to the current source location

    fwc_fraction = {"partial":1.6, "full":0.4}       # max 17kADU with worst case 25e-/ADU gain -> 425ke
    dith_amp = 0.012     # 0.004 is ~a pixel size in deg
                        # change to 0.012 for example if SRON gimbal sensitivity is too coarse
    n_rows is used only in the partial mode

    fov_table     : provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')

    fwc_fraction  : ogse attenuation (sent to ogse.set_fwc_fraction)
    fov_selection : None, or a list (or numpy array) of field of view

    bandpass: IAS: Index in filter wheel 1 of the bandpass filter that is requested (1: Green, 2: Red, 3: NIR).
              SRON, INTA: NotImplemented

    EXAMPLES
    $ execute(cam_tvpt_010, num_subpix=25, num_frames=2, num_bck=2, n_rows=500, fwc_fraction=1.6, mode="partial", dith_amp=0.012, fov_table="reference_full_40", fov_selection=None, bandpass=2)
    $ execute(cam_tvpt_010, num_subpix=25, num_frames=2, num_bck=2, n_rows=None, fwc_fraction=0.4, mode="full", dith_amp=0.012, fov_table="reference_full_40", fov_selection=np.arange(20,30), bandpass=3)
    $ execute(cam_tvpt_010, num_subpix=25, num_frames=2, num_bck=2, n_rows=None, fwc_fraction=0.4, mode="full_E_or_F", dith_amp=0.012, fov_table="reference_full_40", fov_selection=np.arange(20,30), bandpass=3)
    """

    # A. CHECK STARTING CONDITIONS

    if not mode == "partial" and not mode == "full" and not mode == "full_E_or_F":
        raise Abort("The mode parameter is not known. It shall be exclusively: 'partial', or 'full', or 'full_E_or_F'")

    if mode == "partial" and n_rows is None:
        raise Abort("The mode parameter is 'partial', but n_rows is None")

    system_test_if_idle()    # if systen not idle -> Abort is raised

    setup = GlobalState.setup

    # B. DEFINITION TEST PARAMETERS

    if bandpass is None:
        ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)
    else:
        ogse.set_fwc_fraction_bandpass(fwc_fraction=fwc_fraction, bandpass=bandpass)

    # Checking fov_table parameter
    if fov_table is None:
        raise Abort(f"Argument 'fov_table' is None and should be defined.")

    setup = GlobalState.setup
    try:
        tab = setup.fov_positions[fov_table]
    except:
        raise Abort(f"The requested FoV table {fov_table} is not defined in the current setup")

    if len(tab['theta']) == 0 or len(tab['theta']) != len(tab['phi']):
        raise Abort(
            f"The requested FoV table {fov_table} has an invalid format. Theta:{len(tab['theta'])}, Phi:{len(tab['phi'])}")

    use_angles = True
    verbose = True

    ccdrows, ccdcols, ccdcodes, ccdsides, fov_coordinates = fov_test_geometry.fov_geometry_from_table(distorted=True,
                                                                                    distorted_input=False,
                                                                                    table_name=fov_table,
                                                                                    use_angles=use_angles,
                                                                                    verbose=verbose)

    # FOV_SELECTION
    if fov_selection is not None:
        LOGGER.info(f"Selected Field Positions:\n {fov_selection}")
        LOGGER.info(f"Selected Field Positions:\n {fov_coordinates[fov_selection]}")
    else:
        fov_selection = np.arange(len(ccdrows))

    npos = len(fov_selection)

    # C. COMMANDING

    if mode == "partial":

        c = 0
        for posid, position in zip(fov_selection, fov_coordinates[fov_selection]):
            c+=1

            if ccdrows[posid] is None or ccdcols[posid] is None or ccdcodes[posid] is None or ccdsides[posid] is None:
                LOGGER.warning(f"Invalid Selected Field Positions:\n {fov_coordinates[fov_selection]}")
                continue

            # Point CAM to first FoV position
            theta0 = position[0]
            phi0 = position[1]

            LOGGER.info(f"pos {fov_selection[c-1]:2d}  (pos {c:2d}/{npos}). Pointing source to field angles  [{theta0}, {phi0}]")

            point_source_to_fov(theta=theta0, phi=phi0, wait=True)
            visit_field_angles(theta0, phi0)

            # Acquire background images:
            LOGGER.info(f"Acquiring Background frames for the FoV position ({theta0}, {phi0})")

            row_min = int(max(0, ccdrows[posid] - n_rows/2))
            row_max = int(min(4509, ccdrows[posid] + n_rows/2))

            dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, num_cycles=num_bck, row_start=row_min, row_end=row_max,
                                   rows_final_dump=4510,
                                   ccd_order=[ccdcodes[posid], ccdcodes[posid], ccdcodes[posid], ccdcodes[posid]],
                                   ccd_side=ccdsides[posid])

            # IF num_bck=1 is the first of the 4 layers saturated or all 4?
            # If only the first, then I can use num_bck=num_frames=1 instead of 2

            ogse.shutter_open()
            LOGGER.info(f"Acquiring Images for the FoV position ({theta0}, {phi0})")
            dpu.on_frame_number_do(3, dpu.n_cam_partial_ccd, num_cycles=0, row_start=row_min, row_end=row_max,
                                   rows_final_dump=4510,
                                   ccd_order=[ccdcodes[posid], ccdcodes[posid], ccdcodes[posid], ccdcodes[posid]],
                                   ccd_side=ccdsides[posid])

            dpu.wait_cycles(1)
            for subpix in range(num_subpix-1):
                # num_subpix random positions around these x,y coordinates

                # what happens with num_frames=1 ?
                wait_cycles(num_frames-1)   # -1 is needed here as an extra frame is waited by the on_long_pulse_do below
                theta = theta0 + uniform(-dith_amp, dith_amp)
                phi = phi0 + uniform(-dith_amp, dith_amp)
                dpu.on_long_pulse_do(point_source_to_fov, theta=theta, phi=phi, wait=False)

                #output is a single fits file with 25*num_frames*4 layers

            wait_cycles(num_frames)     # this for the last (25th) dither position
            # close shutter and stop acquiring images before moving to next FoV position:

            dpu.n_cam_to_dump_mode()    #needed in the position loop to stop the infinite acquisition loop
            ogse.shutter_close()

    else:
        # this part is the mode acquiring full frames of all 4 CCDs

        ccdorder = {1: [1, 2, 3, 4], 2: [2, 3, 4, 1], 3: [3, 4, 2, 1], 4: [4, 1, 2, 3]}

        c = 0
        for posid, position in zip(fov_selection, fov_coordinates[fov_selection]):
            # visit each angle coordinate within ccd number ccd
            c+=1

            if ccdrows[posid] is None or ccdcols[posid] is None or ccdcodes[posid] is None or ccdsides[posid] is None:
                LOGGER.warning(f"Invalid Selected Field Positions:\n {fov_coordinates[fov_selection]}")
                continue

            if mode == "full":
                ccd_side = "BOTH"
            else:
                ccd_side = ccdsides[posid]
            
            # Point CAM to first FoV position
            theta0 = position[0]
            phi0 = position[1]

            LOGGER.info(f"pos {fov_selection[c-1]:2d}  (pos {c:2d}/{npos}). Pointing source to field angles  [{theta0}, {phi0}]")

            LOGGER.info(f"Pointing source to field angles ({theta0}, {phi0})")
            point_source_to_fov(theta=theta0, phi=phi0, wait=True)
            visit_field_angles(theta0, phi0)

            # Acquire background images:
            LOGGER.info(f"Acquiring Background frames for the FoV position ({theta0}, {phi0})")
            dpu.n_cam_full_ccd(num_cycles=num_bck, ccd_order=ccdorder[ccdcodes[posid]], ccd_side=ccd_side, rows_overscan=0)

            # Start infinite loop of acquisition
            LOGGER.info(f"Acquiring Images for the FoV position ({theta0}, {phi0})")
            ogse.shutter_open()
            dpu.n_cam_full_ccd(num_cycles=0, ccd_order=ccdorder[ccdcodes[posid]], ccd_side=ccd_side, rows_overscan=0)

            dpu.wait_cycles(1)
            for subpix in range(num_subpix):
                # num_subpix random positions around these x,y coordinates

                wait_cycles(num_frames-1)   # -1 is needed here as an extra frame is waited by the on_long_pulse_do below
                theta = theta0 + uniform(-dith_amp, dith_amp)
                phi = phi0 + uniform(-dith_amp, dith_amp)
                dpu.on_long_pulse_do(point_source_to_fov, theta=theta, phi=phi, wait=False)

            wait_cycles(num_frames)     # this for the last (25th) dither position
            # close shutter and stop acquiring images before moving to next FoV position:

            dpu.n_cam_to_dump_mode()    #needed in the position loop to stop the infinite acquisition loop
            ogse.shutter_close()


    # Put the setup back to idle, ready for the next test
    system_to_idle()
