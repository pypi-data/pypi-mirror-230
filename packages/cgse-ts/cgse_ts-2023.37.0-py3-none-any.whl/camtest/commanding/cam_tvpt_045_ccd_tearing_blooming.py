"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

CAM-TVPT-045 CCD characterization



N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in STANDBY
    setup.ogse.calibration.fwc_calibration calibrated to ~ FWC

End status
    NFEE in STANDBY

Synopsis:
    1. Acquire num_dark images
    2. Position the source in the FoV
    3. Set the ogse attenuation according to fwc_fraction
    4. Acquire num_cycles images
    5. Move the source by 1/10 pixel across the column and iterate from 4.
    6. Iterate from 3
    7. Iterate from 2


Authors: P. Royer

Versions:
    2022 06 09 - 0.1 Creation
"""
import time

import numpy as np
from camtest.commanding import LOGGER
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding import dpu
from camtest.core.exec import building_block
from camtest.commanding import ogse
from camtest.commanding import mgse
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates

@building_block
def cam_tvpt_ccd_tear_blooming(num_dark=None, num_cycles=None, mag_list=None, fov_positions=None, num_subpix=None, delta_column=None, ccd_order=None, ccd_both=None):
    """
    cam_tvpt_ccd_tear_blooming(num_dark=None, num_cycles=None, mag_list=None, fov_positions=None, num_subpix=None, delta_column=None, ccd_order=None, ccd_both=None)

    GOAL
    Observe a source at different positions along a row / across a column
    Optionally, repeat at different magnitudes and locations in the field of view.

    Standard observing mode (25sec cycle, 4 CCDs, full frame acquisiton, both sides

    INPUT
    num_dark    : nb of dark images to acquire at the start of the test
    num_cycles  : nb of images (cycles) acquired at every ("dither") position
    mag_list    : magnitudes to be tested. Baseline assumption : FWC-calibration = magnitude 8
    fov_positions: fov_positions where the test should be executed.
                   Format: 2d array or list: [[theta_1, phi_1], [theta_2, phi_2], ...]
    num_subpix  : nb of local "dithers" to be acquired
    delta_column: relative movement, in pixels, across the column, for each dither (e.g. 0.1)
    ccd_both    : True, set ccd_side="BOTH"
                  None or False: ccd_side is computed from the fov_positions

    EXAMPLE
    execute(cam_tvpt_ccd_tear_blooming, num_dark=2, num_cycles=4, mag_list=[10,8,6,4],
            fov_positions=[[8.3,45]], num_subpix=10, delta_column=0.1, ccd_both=None)
    """

    # A. CHECK STARTING CONDITIONS

    # SYSTEM IS IDLE : check system_is_idle, and raise appropriate exception if not
    system_test_if_idle()


    # B. ACQUIRE BACKGROUND IMAGES
    LOGGER.info(f"Acquiring Background frames")
    dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_dark, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                           rows_overscan=0)

    # C. CORE

    for fov in fov_positions:

        for mag in mag_list:

            # INITIAL POSITION
            mgse.point_source_to_fov(theta=fov[0], phi=fov[1], wait=True)

            ccdrows, ccdcols, ccd_codes, ccd_sides = angles_to_ccd_coordinates(angles=np.array([fov]), distorted=True)
            row, column, ccd_code, ccd_side = ccdrows[0], ccdcols[0], ccd_codes[0], ccd_sides[0]

            if ccd_both:
                ccd_side = "BOTH"

            if ccd_order:
                readout_order = ccd_order
            else:
                readout_order = [ccd_code, ccd_code, ccd_code, ccd_code]

            # SET OGSE FLUX
            # translation of magnitude to attenuation with the assumption that mag 8 corresponds to 100% full well
            ogse.set_fwc_fraction(fwc_fraction=pow(10, 0.4 * (8 - mag)))

            # IMAGE ACQUISITION
            # Start infinite loop of acquisition
            LOGGER.info(f"Acquiring Images for the FoV position ({fov[0]}, {fov[1]})")

            ogse.shutter_open()
            dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=readout_order, ccd_side=ccd_side,
                                   rows_overscan=30)

            # SCANNING A COLUMN
            dpu.wait_cycles(1)
            for subpix in range(num_subpix):

                # This returns in cycle num_cycles-1, when you are at frame number 3 (i.e. at the 3rd short pulse)
                dpu.wait_cycles(num_cycles-1)

                # During the readout of last CCD during cycle num_cycles, you move the mechanisms
                dpu.on_long_pulse_do(mgse.point_source_to_ccd_coordinates, row=row, column=column, ccd_code=ccd_code,
                                     wait=False)

                column = column + delta_column

            dpu.wait_cycles(num_cycles)  # this for the last (25th) dither position
            # close shutter and stop acquiring images before moving to next FoV position:

            # END IMAGE ACQUISITION
            dpu.n_cam_to_dump_mode()
            ogse.shutter_close()

    system_to_idle()

