"""
PLATO TVAC TEST CAMPAIGN
HIGH LEVEL TEST SCRIPT FOR TEST
PLATO-KUL-PL-TS-0001
6.9.3 CAM-TVPT-040 Out of field straylight
PLT-N-CAM-1550 and PLT-CAM-922
Start condition:
    Dark conditions in the lab
    OGSE with full attenuation (closed)
    NFEE in DUMP
    Temp stable
    system in idle
End status
    Dark conditions in the lab
    OGSE with full attenuation (closed)
    NFEE in DUMP
    Temp stable
    system in idle
Synopsis for test execution:
    - for test cases (OoF, FOV edge) set the angle from the optical axis
        - for ogse source position (off-axis angle for test case and set of azimuth angles)
        - n_cam_full_image_standard - dark images
        - ogse_set_attenation
        - n_cam_full_image_standard - straylight images
    - closure of test
    - in-field straylight measurements are acquired as product of other tests; analysis will be prepared for CAM-TVPT-Test 090 - ghost measurements
    - combination with vignetting test TBD

Versions:
    2021 01 13 - 0.1 Draft -- Creation based on 010, 030, and 050 to prepare next discussion 		  -- T. Kanitz -- TK
    2021 02 28 - 0.2 Draft -- Updating 									                              -- T. Kanitz -- TK
        - remove *ogse_swon and *ogse_swoff with shutter to keep ogse source stable (telco 17 Feb 2021, ND Filters)
        - adding placeholders for wait and check test setup before execution
        - adding placeholders for wait and check acquisition
        - adding placeholder for final check after test (telco 26 Feb 2021, Ghosts)
        - using currently for "sites" IAS, SRON, INTA
    2021 03 03 - 0.3 Draft -- Updating TODO item on OoF and IF straylight							  -- T. Kanitz -- TK
    2021 03 17 - 0.4 Draft -- Rename dpu.ncam_full_image into dpu.n_cam_partial_ccd (github issue 104)
    2021 05 05 - 0.5 Draft -- Updating  PLATO-KUL-PL-MAN-0004 v0.3 iteration                          -- T. Kanitz -- TK
        - replace shutter handling with ogse attenuation
        - replace common 360 deg azimuth scan for gimbal sides via site dependent dict based on telco Ghosts
        and Straylight early 2021
        - removed infield straylight measurements with FOV edge measurements
        - remove check for dump mode at the begin and set nfee to dump at the end
        - use ncam full standard for acquisition
    2021 06 13 - 0.6 Draft -- Updating  PLATO-KUL-PL-MAN-0004 v0.4 iteration                          -- T. Kanitz -- TK
        - and copy paste from ghost script, dark script, demo_basic
        - remove load_setup Sec. 7.3; is done only once at start test phase
        - introduce system_test idle at begin and end according to Sec. 14
        - replace while temp_stabil dummy with tcs.wait_camera_stable according to ghost and found in tcs.py
        - false loop in dictionary corrected
        - replace num_frames with specific bck acquisition number (different position -> temperature)
        - replace acquisition kept "ALT"
        - replace ogse.att_close with shutter_close, Sec. 13.4
        - replace dpu.nfee to dump with system_to_idle, Sec. 14
    2021 06 27 - 0.7 Draft -- Updating  after test rehearsal iteration                                -- T. Kanitz -- TK
        - no need of move_to_position.yaml -> remove comment
        - system_to_idle and if_idle used at start and end of test
        - change max angle for hexapod to 23deg
        - remove tcs.wait_camera_stable()
        - remove hexapod IAS move_to_position as a specific hexapod call will be needed -> Claudia opened GIT question
        - same number for straylight and bkg measurements
        - use acquisition "BOTH" to save time
        - remove dpu.waits
        - add shutter_open before set_attenuation
        # Angles
        - add angles to scan the are of the strap connections (email exchange 27 Apr, 11:00) and reminder by Bart
        - transfer the script from a loop to the different objectives in the call
        # intensities
        - based on Pierres feedback 17/6/2021, using ogse_set_attenuation(fwc=fraction=1./GlobalState.setup.gse.ogse.fwc_calibration)
    2021 10 20 - 0.8 Draft -- Using the new names from the OGSE commanding                                     -- KUL
    2021 10 26 - 0.9 Draft -- Last Update before final discussion                                     -- T. Kanitz -- TK
        - meeting with Antoine, Martin, Matteo on 20 July 2021 -> no dedicated calls for hexapod required for SRON
            - update angles to window of 90deg only and off axis angles to OoF only -> overlap with ghosts, vignetting
            - added angle for Flexi
            - updated ogse.ogse_set_attenuation to ogse.ogse_set_attenuation_level
            - harmonised OoF/ooF to ooF everywhere
            - cleaning: removal of numpy call
            - after Best Focus Discussion 26/10/2021 put fwc factor into execute line
    2021 10 29 - 1.0 Final discussion before Sron				                                     -- T. Kanitz -- TK
        - meeting with 29/10/2021 - minor changes
            - update angles to window of 90deg only and off axis angles to OoF only -> overlap with ghosts, vignetting
    2022 02 28 - 1.1 Update before execution at SRON			                                     -- N. Gorius
        - update to add more flexibility on test configuration: azimuth offset, number of darks, maximum amplitude
        to adapt to limitation of SRON gimbal during EM test.
        - aligned parameters names with names used in TVPT-010 and TVPT-090
    2022 03 01 - 1.2 Update after first execution at SRON			                                     -- N. Gorius
        - limit switch triggering require more flexibility on the visited position, including:
            - entry of azimuth list via argument instead of hardcoded values
            - added manual pick of elevation position
    2022 06 24 - 1.3 Update before IAS test			                                                    -- T. Kanitz
        - make commanding completely independent of objective


Open points:
    - TODOs in script
        - hexapod offset position
        - alignment to Vignetting test
        - FCAM calls
"""

# #######################################################################################################
# ## packages ###########################################################################################
# ## loading packages from camtest ######################################################################
import logging

from camtest import building_block  # adjusted according to demo_basic 20210612
from camtest.commanding import dpu  # acquisition
from camtest.commanding import mgse  # mgse
from camtest.commanding import ogse  # shutter/attention
from camtest.commanding import system_test_if_idle, system_to_idle  # Command Manual v0.4 Sec. 14
from egse.state import GlobalState  # adjusted according to demo_basic 20210612
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


# ## loading standard packages within requirements/develop ##############################################

# #######################################################################################################
# ## building block #####################################################################################


@building_block
def cam_tvpt_040_straylight(num_frames=None, num_bck=None, fwc_list=None, phi_list=None, theta_list=None):
    """
    SYNOPSIS
    cam_tvpt_040(num_frames=15,num_bck=15,ooF_objective='oof_moon',fwc_list=None, phi_list=None, theta_list=None)
    num_frames : number of lit frames per FoV position;
    num_bck: number of background acquisition per FoV position;
    fwc_list: [float,float,...]
    phi_list: [float,float,...]
    theta_list: [float,float,...]

    Acquisition
        - depending on MGSE (gimbal,hexapod) for the angle from the optical axis [edge 1-4] at x-y position
        ([0,0],[function of azimuth])
        - acquire at different azimuth positions
        1. dark measurement with ogse full attenuation
        2. straylight measurement with OGSE TBD attenuation
        - Priority should be given to a scan of 0-90deg Azimuth with as many as possible LOS-Offaxis angles outside the FOV as possible
            - allow same measurements at all three THs (comparison)
            - this will cover the potentially sensitive AOI at L6 or the flexis
            - lower priority to AOI changes compared to x-y offsets
            - Add for at least EM max x-y offset settings for a measurement to confirm the robustness of the test
            - Additional smaller steps in x-y offset for sensitivity analysis with lowest priority.

    EXAMPLES
    For SRON and INTA
    $ execute(cam_tvpt_040_straylight,num_frames=15,num_bck=15) # 15 * 25s (full_standard) * 4 azimuths * 3 executions = 75min  (3execution bkg and straylight and saturated)
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-180],theta_list=[19.,19.33,19.65,20.]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-175],theta_list=[19.,19.33,19.65,20.]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-135],theta_list=[19.,19.3]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[4000],phi_list=[-152,-149,-142,-135],theta_list=[19.65,20.]) #
    For IAS
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-180],theta_list=[19.,20.,21.,22.,23.]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-175],theta_list=[19.,20.,21.,22.,23.]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[400,4000],phi_list=[-135],theta_list=[19.,19.3,23]) #
    $ execute(cam_tvpt_040_straylight,num_frames=6,num_bck=6,fwc_list=[4000],phi_list=[-152,-149,-142,-135],theta_list=[19.65,20.,20.5,21.,21.5,22.,22.35]) #
    """

    # B. OPTIONAL? Load setup
    setup = GlobalState.setup  # load_setup done, Sec. 7.3, but given like demo_basic
    site = setup.site_id  # adjusted according to demo_basic 20210612
    LOGGER.info(f"CAM-TVPT-040 Start for {site}")  # adjusted according to demo_basic 20210612

    # A. CHECK STARTING CONDITIONS
    # A1 Check CAM
    system_test_if_idle()  # FEE in dump, OGSE shutter close, filter unknown, TCS on, MGSE ready Sec. 14, 20210612
    # no check on temperature stability;
    # test wont be executed before temperature stability is not reached per overall procedure

    # ##################################################################################################################
    # Test specific steps
    # C. DEFINITION TEST PARAMETERS
    #           1) the FWC for set_attenuation, float
    #           2) the theta angles for point_source_to_fov, float
    #           3) the phi angles for point_source_to_fov, list of float for loop

    # ## measurements at 0, 90deg and 18.88deg will be performed with different intensities within the Ghost test
    # ## measurements at 45deg and TBD are supposed to be done within the vignetting test
    # ## moved start of the OoF measurements to start at 19deg
    # ## kept the angles at 0, 45, 90 deg for the PST
    # ## added angle at 5deg for Flexi
    # ## 65deg optional for F-CAMs and vignetting test overlap (IAS only)
    # ##

    # D. COMMANDING
    # loop over azimuth angles
    for azimuth in phi_list:

        ogse.set_fwc_fraction(fwc_fraction=fwc_list[0])

        # MGSE move
        # loop over elevation angles
        for elevation in theta_list:
            LOGGER.info(f"CAM-TVPT-040 Pointing source to field angles ({elevation},{azimuth})")
            mgse.point_source_to_fov(theta=elevation, phi=azimuth, wait=True)
            visit_field_angles(elevation, azimuth)

            # Dark measurement
            LOGGER.info(f"CAM-TVPT-040 Starting Dark Measurement")
            # TODO F-CAM
            dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_bck, ccd_side="BOTH")

            # Straylight measurement
            # loop over intensity settings
            for fwc_set in fwc_list:
                LOGGER.info(f"CAM-TVPT-040 Starting Straylight Measurement ({fwc_set})")
                ogse.set_fwc_fraction(fwc_fraction=fwc_set)
                ogse.shutter_open()
                dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_frames, ccd_side="BOTH")
                ogse.shutter_close()

    LOGGER.info(f"CAM-TVPT-040 Finish")

    system_to_idle()  # FEE in dump, OGSE shutter close, filter unknown TCS on, MGSE ready Sec. 14
