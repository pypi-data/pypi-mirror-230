"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

PLATO-INAF-PL-TS-0003
9.18 CAM-TVPT-050 EMC autocompatibility test

PLATO-DLR-PL-RP-0001 section 5.3.2 allocates 5 electrons to EMC noise per camera.

Test configuration:
    • Camera units: ON, readout mode: external sync
    • OGSE: ON
    • MGSE: ON

Start condition:
    Dark conditions in the lab
    NFEE in DUMP
    Temp stable

End status
    NFEE in DUMP

Synopsis for test execution:
    At BFT temperature plateau
    Set TCS to Nominal Mode (Extended mode)
        Acquire Dark Background Images
        Acquire Charge Injected Images
        Acquire Dark Background Images
    Set TCS to Off Mode (Calibration Mode)
        Acquire Dark Background Images
        Acquire Charge Injected Images
        Acquire Dark Background Images
    Set TCS to Nominal Mode (Extended mode)

Allows for having a source during charge injection, and a low level full-image charge injection

Versions:
    2021 05 05 - 0.1 Draft -- Creation based on 040, PLATO-KUL-PL-MAN-0004	                -- T. Kanitz -- TK
    2021 06 12 - 0.3 Draft -- Creation based on 040 update and PLATO-KUL-PL-MAN-0004, v0.4  -- T. Kanitz -- TK
    2021 06 27 - 0.7 Draft -- Updating  after test rehearsal iteration                      -- T. Kanitz -- TK
        - remove tcs.wait, dpu.wait, use system_to_idle and if_idle, col_end from charge_injection
        - increase number of acquisition by *2 for ALT acquisition
    2022 01 21 - 0.8 Draft -- Replacing "ALT" with "BOTH"                                   -- S. Regibo -- SR
    2022 01 25 - 0.9 Draft -- Replacing NORMAL with EXTENDED in TCS commands (issue TS-508) -- P. Royer -- PR
    2023 04 29 - 0.10 Draft -- Rewritten for PFM testing, to reflect new TS.                -- C. Arena -- CA
        - fixes a missing dark acquisition. Now dark are acquire both before and after each of the two CI
        - allows for a source during charge injection
        - allow for charge injections for a fixed numbers of rows, or over all the image
        - clean up logging

"""
import logging
import time


from camtest.commanding import dpu, tcs, ogse  # acquisition
from camtest.commanding import system_test_if_idle, system_to_idle  # Command Manual v0.4 Sec. 14 -> NOT FOUND
from camtest.core.exec import building_block  # adjusted according to demo_basic 20210612
# #######################################################################################################
# ## packages ###########################################################################################
# ## loading packages from camtest ######################################################################
from egse.state import GlobalState  # adjusted according to demo_basic 20210612
from egse.tcs import OperatingMode
from camtest.commanding.mgse import point_source_to_fov
from camtest.commanding.functions.fov_test_geometry import ccd_coordinates_to_angles
from egse.exceptions import Abort
from egse.visitedpositions import visit_field_angles
LOGGER = logging.getLogger(__name__)

# ## loading standard packages within requirements/develop ##############################################


# #######################################################################################################
# ## building block #####################################################################################


@building_block
def cam_tvpt_050(cam_num_frames=None, cam_num_bck=None, bck_sides=None, ci_width=None, ci_gap=None, ci_vgd=None, source=None, fwc_fraction=None, bandpass=None, ccd_code=None, row=None, column=None):
    """
    SYNOPSIS
    cam_tvpt_050(cam_num_frames=10, cam_num_bck=10, bck_sides='BOTH', ci_width=200, ci_gap=200, ci_vgd=16, source=True,
     fwc_fraction=0.3, bandpass=None, ccd_code=1, row=2498, column=1000)
    Charge injection:
            - n_cam_charge_injection_full
    Change of TCS on/off:
            - n_cam_full_image_standard
            - tcs from nominal to calibration mode
            - n_cam_full_image_standard
            - tcs from calibration to nominal mode
            - n_cam_full_image_standard
    Args:
        cam_num_frames: int, Number of CI images to acquire, in each of the two TCS modes.
                        Total number of CI frames acquire = 2 * cam_num_frames
        cam_num_bck : int Number of background images to acquire, both before and after CI frames.
                        Total number of background frames acquired: 4 * cam_num_bck
        bck_sides: CCD side to acquire for background images. This can be 'BOTH' (acquire E and F at the same time), 'E', 'F, 'EF' (acquire E first, and then F) or 'FE'.
        ci_width: int, width in rows of the regions with charge injections, typically 100 (see ci_gap), or 4510 for full injection
        ci_gap:   int, width in rows of the regions without charge injections, typically 100

        ci_type : str, 'bands' to get 100 rows regions of charge injections, spaced by 100 rows of no charge injection
                        'full' to get a full charge injection image

        ci_vgd      : V_GD voltage, driving charge-injection level
                    V_GD ~ 14 : FWC
                    V_GD = 15 ~ 70% FWC
                    V_GD = 16 ~ 50% FWC
                    V_GD = 17 ~ 30% FWC
        source  : bool, True if we want a source during charge injection, False or not otherwise
        fwc_fraction  : ogse attenuation (sent to ogse.set_fwc_fraction)
        bandpass: IAS: Index in filter wheel 1 of the bandpass filter that is requested (1: Green, 2: Red, 3: NIR).
          SRON, INTA : NotImplemented
        ccd_code: int, CCD code associated with the position of the source. This needs to be a single value
        row     : int, row position of the source. This needs to be a single position
        column  : column, column position of the source. This needs to be a single position

    EXAMPLE
    $ execute(cam_tvpt_050, cam_num_frames=10, cam_num_bck=10, bck_sides='BOTH', ci_width=100, ci_gap=100, ci_vgd=17,
    source=True, fwc_fraction=0.5, bandpass=None, ccd_code=1, row=1000, column=1000,
    description="TVPT-050 EMC autocompatibility - with source")

    $ execute(cam_tvpt_050, cam_num_frames=10, cam_num_bck=10, bck_sides='BOTH', ci_width=4510, ci_gap=0, ci_vgd=17,
    source=False, fwc_fraction=None, bandpass=None, ccd_code=None, row=None, column=None,
    description="TVPT-050 EMC autocompatibility - full image CI")

    """
    def acquire_bck():
        if bck_sides in ['BOTH', 'E', 'F']:
            dpu.n_cam_full_standard(num_cycles=cam_num_bck, ccd_side=bck_sides)
        elif bck_sides is 'EF':
            dpu.n_cam_full_standard(num_cycles=cam_num_bck, ccd_side='E')
            dpu.n_cam_full_standard(num_cycles=cam_num_bck, ccd_side='F')
        elif bck_sides is 'FE':
            dpu.n_cam_full_standard(num_cycles=cam_num_bck, ccd_side='F')
            dpu.n_cam_full_standard(num_cycles=cam_num_bck, ccd_side='E')

    # A.    Load setup
    setup = GlobalState.setup							# load_setup already performed, Sec. 7.3, but given in demo
    site = setup.site_id								# adjusted according to demo_basic 20210612
    LOGGER.info(f"Executing CAM-TVPT-050 for {site}")   # adjusted according to demo_basic 20210612

    # B.    CHECK STARTING CONDITIONS
    # B1    Check CAM
    system_test_if_idle()	  # FEE in dump, OGSE shutter close, filter unknown, TCS on, MGSE ready Sec. 14, 20210612
    ##TODO: is TCS really in extended mode? Can we check and abort if not?

    # #################################################################################################################
    # Test specific steps
    # C.    DEFINITION TEST PARAMETERS
    cam_start = 0
    cam_stop = 4510
    cam_ccd_order = [1, 2, 3, 4]

    if cam_num_frames == 0 or cam_num_frames is None:
        raise Abort(f"Argument 'cam_num_frames' is a non-valid value")

    if source is True:

        LOGGER.info(f"Setting fwc to {fwc_fraction}")

        if bandpass is None:
            ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)
        else:
            ogse.set_fwc_fraction_bandpass(fwc_fraction=fwc_fraction, bandpass=bandpass)

        # POSITION INFO
        angles = ccd_coordinates_to_angles(ccdrows=[row], ccdcols=[column], ccdcodes=[ccd_code], verbose=False)
        theta = angles[0, 0]
        phi = angles[0, 1]

        LOGGER.info(f"Pointing to:")
        LOGGER.info(f"          CCD {ccd_code}, [row,col]=[{row},{column}]")
        LOGGER.info(f"          FoV angles [theta,phi]=[{theta:6.2f},{phi:6.2f}])")

        point_source_to_fov(theta=theta, phi=phi, wait=True)
        visit_field_angles(theta, phi)

    # D.    COMMANDING

    # ########### TCS extended mode ###########

    # D1.1  Background acquisition
    LOGGER.info(f"Starting background acquisition, TCS in extended mode, before Charge Injection acquisition")
    acquire_bck()  # TCS on, before CI background

    # D1.2  Charge Injection
    LOGGER.info(f"Starting Charge Injection acquisition, with TCS in extended mode")
    if source is True:
        ogse.shutter_open()

    dpu.n_cam_charge_injection_full(
        num_cycles=cam_num_frames, row_start=cam_start, row_end=cam_stop,
        rows_final_dump=0, ccd_order=cam_ccd_order, ccd_side="BOTH",
        ci_width=ci_width, ci_gap=ci_gap, vgd=ci_vgd)

    if source is True:
        ogse.shutter_close()
        time.sleep(2)

    # D1.3  Background acquisition
    LOGGER.info(f"Starting background acquisition, TCS in extended mode, after Charge Injection acquisition")
    acquire_bck()  # TCS on, after CI background

    # D2    TCS changing to calibration mode
    LOGGER.info(f"Setting TCS to calibration mode...")
    tcs.stop_task()
    time.sleep(5)
    while tcs.is_task_running() is True:
        time.sleep(1)

    tcs.set_operating_mode(mode=OperatingMode.CALIBRATION)
    tcs.start_task()

    # ########### TCS calibration mode ###########

    # D3.1  Background acquisition
    LOGGER.info(f"Starting background acquisition, TCS in calibration mode, before Charge Injection acquisition")
    acquire_bck()  # TCS off, before CI background

    # D3.2  Charge Injection
    LOGGER.info(f"Starting Charge Injection acquisition, with TCS in calibration mode")
    if source is True:
        ogse.shutter_open()

    dpu.n_cam_charge_injection_full(
        num_cycles=cam_num_frames, row_start=cam_start, row_end=cam_stop,
        rows_final_dump=0, ccd_order=cam_ccd_order, ccd_side="BOTH",
        ci_width=ci_width, ci_gap=ci_gap, vgd=ci_vgd)

    if source is True:
        ogse.shutter_close()
        time.sleep(2)

    # D3.3  Background acquisition
    LOGGER.info(f"Starting background acquisition, TCS in calibration mode, after Charge Injection acquisition")
    acquire_bck()  # TCS off, after CI background

    # D4    Return TCS of extended mode
    LOGGER.info(f"Setting TCS back to extended mode...")
    tcs.stop_task()
    time.sleep(5)
    while tcs.is_task_running() is True:
        time.sleep(1)
        
    tcs.set_operating_mode(mode=OperatingMode.EXTENDED)
    tcs.start_task()

    # E Test end
    LOGGER.info(f"Exit CAM-TVPT-050")
    system_to_idle()   		# FEE in dump, OGSE shutter close, filter unknown TCS on, MGSE ready Sec. 14, 20210612