"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

CAM-TVPT-045 CCD characterization

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in DUMP mode

End status
    NFEE in DUMP mode

GOAL
    Observe a source on a raster, expressed in pixel coordinates, no dither
    Optionally repeat on some other CCD(s)

    Observing mode : 25sec cycle (6.25 sec integration), 1 half-CCDs, full frame

INPUTS
    num_cycles  : nb of images (cycles) acquired at every position
    ccds        : list of CCDs to be visited
    row_start, row_step, n_rows : raster parameters wrt rows
    col_start, col_step, n_cols : raster parameters wrt columns
    fwc_fraction: OGSE attenuation factor (relative to the setup's fwc_calibration)

DURATION
    n_rows * n_cols * len(ccds) * num_cycles * 25 seconds + MGSE movements

EXAMPLE : single row in the middle of all CCDs, every 150 pixels

    execute(cam_tvpt_ccd_pixel_grid, num_cycles=2, ccds=[1,2,3,4], row_start=2250, row_step=0, n_rows=1, col_start=150, col_step=150, n_cols=29, fwc_fraction=0.001)


Authors: P. Royer

Versions:
    2022 07 14 - 0.1 Creation
"""

from camtest.commanding import LOGGER
from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding import dpu
from camtest.core.exec import building_block
from camtest.commanding import ogse
from camtest.commanding import mgse
from camtest.commanding.functions.fov_test_geometry import ccd_coordinates_to_angles
from egse.state import GlobalState


@building_block
def cam_tvpt_ccd_pixel_grid(num_cycles=None,  ccds=None, row_start=None, row_step=None, n_rows=None, col_start=None, col_step=None, n_cols=None, fwc_fraction=None):
    """

    GOAL
    Observe a source on a raster, expressed in pixel coordinates, no dither
    Optionally repeat on some other CCD(s)

    Observing mode : 25sec cycle (6.25 sec integration), 1 half-CCDs, full frame

    INPUTS
    num_cycles  : nb of images (cycles) acquired at every position
    ccds        : list of CCDs to be visited
    row_start, row_step, n_rows : raster parameters wrt rows
    col_start, col_step, n_cols : raster parameters wrt columns
    fwc_fraction: OGSE attenuation factor (relative to the setup's fwc_calibration)

    DURATION
    n_rows * n_cols * len(ccds) * num_cycles * 25 seconds + MGSE movements

    EXAMPLE : single row in the middle of all CCDs, every 150 pixels

    execute(cam_tvpt_ccd_pixel_grid, num_cycles=2, ccds=[1,2,3,4], row_start=2250, row_step=0, n_rows=1, col_start=150, col_step=150, n_cols=29, fwc_fraction=0.001)

    """

    # A. CHECK STARTING CONDITIONS

    # SYSTEM IS IDLE : check system_is_idle, and raise appropriate exception if not
    system_test_if_idle()

    # B. SET OGSE ATTENUATION
    ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)

    # C. BASIC PARAMETER CHECK
    row_min = min(row_start, (row_start + n_rows * row_step))
    col_min = min(col_start, (col_start + n_cols * col_step))
    row_max = max(row_start, (row_start + n_rows * row_step))
    col_max = max(col_start, (col_start + n_cols * col_step))
    if (row_min < 0) or (col_min < 0):
        LOGGER.info(f" {row_min=} {col_min=}")
        LOGGER.info(" CRITICAL -- RASTER GRID VISITS NEGATIVE ROW OR COLUMN. ABORTING")
        return
    if (row_max > 4510) or (col_max > 4510):
        LOGGER.info(f" {row_max=} {col_max=}")
        LOGGER.info(" CRITICAL -- RASTER GRID EXTENDS BEYOND ROW OR COLUMN=4510. ABORTING")
        return

    # D. CORE
    n_pos = n_rows * n_cols * len(ccds)

    LOGGER.info(f"  Estimated duration: {n_pos * num_cycles * 25} seconds + MGSE movements")

    fee_side = GlobalState.setup.camera.fee.ccd_sides.enum

    pos = 0
    for ccd_code in ccds:

        readout_order = [ccd_code, ccd_code, ccd_code, ccd_code]

        for i_row in range(n_rows):

            row = row_start + i_row * row_step

            for i_col in range(n_cols):

                column = col_start + i_col * col_step

                if column >= 2255:
                    ccd_side = fee_side.RIGHT_SIDE.name
                else:
                    ccd_side = fee_side.LEFT_SIDE.name

                # POSITION INFO
                angles = ccd_coordinates_to_angles(ccdrows=[row], ccdcols=[column], ccdcodes=[ccd_code], verbose=False)
                LOGGER.info(f" POSITION {pos}/{n_pos}")
                LOGGER.info(f"          CCD {ccd_code}{ccd_side}, [row,col]=[{row},{column}]")
                LOGGER.info(f"          FoV angles [theta,phi]=[{angles[0,0]:6.2f},{angles[0,1]:6.2f}])")
                pos += 1

                # MOVING TO LOCATION
                LOGGER.info("          START MOVING")
                mgse.point_source_to_ccd_coordinates(row=row, column=column, ccd_code=ccd_code, wait=True)

                # IMAGE ACQUISITION
                LOGGER.info("          START IMAGE ACQUISITION")

                ogse.shutter_open()

                # Issue command at 3rd short pulse -> takes effect at the next long pulse
                dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_cycles, ccd_order=readout_order,
                                       ccd_side=ccd_side, rows_overscan=30)

                ogse.shutter_close()

    system_to_idle()

