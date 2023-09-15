"""
PLATO TVAC TEST CAMPAIGN

HIGH LEVEL TEST SCRIPT FOR TEST

CAM-TVPT-140 Contamination Impact Assessment

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    NFEE in DUMP mode

End status
    NFEE in DUMP mode

GOAL
    This test will observe two large particle contaminants located on the FPA CCDs with a spot light source to assess:
        1. Light blocking fraction of a contaminant,
        2. Near-field scattering from a contaminant, and
        3. Diffuse scattering from a contaminant.

    The overall goal of the test is to assess a potential impact large contaminants may
    have on science performance, e.g. because of lost pixels or increased noise.

    Observing mode : external sync, full readout mode using 1 or 4 CCD(s), recording both or single side.
    
    Positions are explored using column as fast coordinate and row as slow coordinate
    
INPUTS
    mag_list    : list of float, list of flux magnitude to be used
    num_frames    : int, nb of images acquired at every single position
    num_bck       : int, nb of background images acquired
    mode          : str, either 'full' or 'full_E_or_F' or 'single', or 'single_E_or_F', recording
                            all 4 (full...) or single one (single...)
                            and
                            BOTH side of the CCDs,
                            or side associated with the current requested row/col position pair (_E_or_F).
    ccd_code      : int, CCD code to be acquired (1,2,3,4)
    row_start, row_step, n_rows : raster parameters wrt rows
    col_start, col_step, n_cols : raster parameters wrt columns

DURATION
    (n_rows * n_cols * num_frames + num_bck) * 25 seconds + MGSE movements

EXAMPLE

 *  Case#1: FM1 contaminant on CCD3F
        Per S. Niemi doc, CCD_testing_RF (1216,601), grid size 8, step 2
        ->  col_start=1216 -1 -2*(8/2-1)=1209
            row_start= 601 -1 -2*(8/2-1)= 594
    
    execute(cam_tvpt_140_contamination, mag_list=[1., 8.5], num_frames=3, num_bck=3, mode='full', ccd_code=3, col_start=1209, col_step=2, n_cols=8, row_start=594, row_step=2, n_rows=8, description="FM1 contaminant on CCD3F")
    
 *  Case#2: FM1 contaminant on CCD1E
        Per S. Niemi doc, CCD_testing_RF (3942,1742)
        ->  col_start=3942 -1 -2*(8/2-1)=3935
            row_start=1742 -1 -2*(8/2-1)=1735
    
    execute(cam_tvpt_140_contamination, mag_list=[1., 8.5], num_frames=3, num_bck=3, mode='full', ccd_code=1, col_start=3935, col_step=2, n_cols=8, row_start=1735, row_step=2, n_rows=8, description="FM1 contaminant on CCD1E")
    
 *  Case#3: FM1 contaminant on CCD4E
        Per S. Niemi doc, CCD_testing_RF (4242,4456)
        ->  col_start=4242 -1 -2*(8/2-1)=4235
            row_start=4456 -1 -2*(8/2-1)=4449
    
    execute(cam_tvpt_140_contamination, mag_list=[1., 8.5], num_frames=3, num_bck=3, mode='full', ccd_code=4, col_start=4235, col_step=2, n_cols=8, row_start=4449, row_step=2, n_rows=8,  description="FM1 contaminant on CCD4E")
    
Authors: N. Gorius

Versions:
    2023 06 28 - 1.0 First release for FM1 model
"""

import time
import logging

from camtest.commanding import system_test_if_idle, system_to_idle
from camtest.commanding import dpu
from camtest.core.exec import building_block
from camtest.commanding import ogse
from camtest.commanding import mgse
from camtest.commanding.functions.fov_test_geometry import ccd_coordinates_to_angles
from egse.exceptions import Abort
from egse.state import GlobalState

LOGGER = logging.getLogger(__name__)

@building_block
def cam_tvpt_140_contamination(mag_list = None, num_frames=None,  num_bck=None, mode=None, ccd_code=None, row_start=None, row_step=None, n_rows=None, col_start=None, col_step=None, n_cols=None):

    # Check user inputs
    if not mode == "full" and not mode == "full_E_or_F" and not mode == "single" and not mode == "single_E_or_F":
        raise Abort(f"The 'mode' parameter is not known. It shall be exclusively: 'full', or 'full_E_or_F', or 'single', or 'single_E_or_F'. Input: {mode=}. Input: {mode}")

    if not ccd_code in [1,2,3,4]:
        raise Abort(f"The 'ccd_code' is not valid. It shall be exclusively: 1, 2, 3 or 4. Input: {ccd_code=}")
    ccd_code = int(ccd_code)
    
    row_min = min(row_start, (row_start + n_rows * row_step))
    col_min = min(col_start, (col_start + n_cols * col_step))
    row_max = max(row_start, (row_start + n_rows * row_step))
    col_max = max(col_start, (col_start + n_cols * col_step))
    
    LOGGER.info(f" {row_min=} {col_min=}")
    if (row_min < 0) or (col_min < 0):
        raise Abort(f"Commanded positions include negative row_min or col_min. {row_min=} {col_min=}")
        
    LOGGER.info(f" {row_max=} {col_max=} [excluded]")
    if (row_max > 4510) or (col_max > 4510):
        raise Abort(f"Commanded positions include out-of-bound (>4510) row_max or col_max. {row_max=} {col_max=}")
    
    # Check system status
    LOGGER.info(f"   Closing shutter")
    ogse.shutter_close()
                    
    dpu.n_cam_to_dump_mode()
    while not dpu.n_cam_is_dump_mode() and not dpu.n_cam_is_ext_sync():
        time.sleep(1.)

    system_test_if_idle()

    # Main
    n_pos = n_rows * n_cols

    LOGGER.info(f" Estimated duration: {(n_pos * num_frames + num_bck) * 25} seconds + MGSE movements")

    setup = GlobalState.setup
    fee_side = setup.camera.fee.ccd_sides.enum
    col_end = setup.camera.fee.col_end

    pos = 0
    if mode == "full" or mode == "full_E_or_F":
        ccdorder = {1: [1, 2, 3, 4], 2: [2, 3, 4, 1], 3: [3, 4, 2, 1], 4: [4, 1, 2, 3]}
    else:
        ccdorder = {1: [1, 1, 1, 1], 2: [2, 2, 2, 2], 3: [3, 3, 3, 3], 4: [4, 4, 4, 4]}
    
    for i_row in range(n_rows):

        row = row_start + i_row * row_step

        for i_col in range(n_cols):

            column = col_start + i_col * col_step

            if column > col_end:
                ccd_side = fee_side.RIGHT_SIDE.name
            else:
                ccd_side = fee_side.LEFT_SIDE.name
            
            # POSITION INFO
            angles = ccd_coordinates_to_angles(ccdrows=[row], ccdcols=[column], ccdcodes=[ccd_code], verbose=False)
            LOGGER.info(f" Position {pos}/{n_pos}")
            LOGGER.info(f"     CCD {ccd_code}{ccd_side}, [row,col]=[{row},{column}]")
            LOGGER.info(f"     FoV angles [theta,phi]=[{angles[0,0]:6.2f},{angles[0,1]:6.2f}])")
            
            # MOVING TO LOCATION
            LOGGER.info("   MGSE moving...")
            mgse.point_source_to_ccd_coordinates(row=row, column=column, ccd_code=ccd_code, wait=True)
            LOGGER.info("   MGSE in position")
            
            if mode == "full" or mode == "single":
                ccd_side = "BOTH"
           
            if num_bck != 0 and pos == 0:
                LOGGER.info(f"   Acquiring {num_bck} background frames ccdorder={ccdorder[ccd_code]} ccd_side={ccd_side} ...")
    
                dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_bck, ccd_order=ccdorder[ccd_code],
                                       ccd_side=ccd_side, rows_overscan=0)
    
                LOGGER.info(f"   Acquiring {num_bck} background frames - done")
                
                LOGGER.info(f"   Switch to DUMP mode.")
                dpu.n_cam_to_dump_mode()
                while not dpu.n_cam_is_dump_mode():
                    time.sleep(1.)

            # IMAGE ACQUISITION
            for mag in mag_list:
                fwc_fraction = pow(10, 0.4 * (8 - mag))
                LOGGER.info(f"   Filter: {fwc_fraction=} {mag=}")
                ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)
                ogse.shutter_open()
                dpu.wait_cycles(1) # Give time for filter wheel to get in position
                
                # Issue command at 3rd short pulse -> takes effect at the next long pulse
                LOGGER.info(f"   Acquiring {num_frames} lit frames ccdorder={ccdorder[ccd_code]} ccd_side={ccd_side} ...")
                dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_frames, ccd_order=ccdorder[ccd_code],
                                       ccd_side=ccd_side, rows_overscan=0)
                LOGGER.info(f"   Acquiring {num_frames} lit frames - done")
                LOGGER.info(f"   Closing shutter")
                ogse.shutter_close()
                
                LOGGER.info(f"   Switch to DUMP mode.")
                dpu.n_cam_to_dump_mode()
                while not dpu.n_cam_is_dump_mode():
                    time.sleep(1.)
            
            # Increment position index tracking
            pos += 1
        

    system_to_idle()

