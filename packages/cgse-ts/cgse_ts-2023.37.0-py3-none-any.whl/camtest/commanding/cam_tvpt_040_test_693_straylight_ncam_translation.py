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
    2021 01 13 - 0.1 Draft -- Creation based on 010, 030, and 050 to prepare next discussion        -- T. Kanitz -- TK
    2021 02 28 - 0.2 Draft -- Updating                                                           -- T. Kanitz -- TK
        - remove *ogse_swon and *ogse_swoff with shutter to keep ogse source stable (telco 17 Feb 2021, ND Filters)
        - adding placeholders for wait and check test setup before execution
        - adding placeholders for wait and check acquisition
        - adding placeholder for final check after test (telco 26 Feb 2021, Ghosts)
        - using currently for "sites" IAS, SRON, INTA
    2021 03 03 - 0.3 Draft -- Updating TODO item on OoF and IF straylight                      -- T. Kanitz -- TK
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
    2021 10 29 - 1.0 Final discussion before Sron                                                -- T. Kanitz -- TK
        - meeting with 29/10/2021 - minor changes
            - update angles to window of 90deg only and off axis angles to OoF only -> overlap with ghosts, vignetting
    2022 07 25 - 1.1 Translation added in an IAS version with hexapod -- P. Guiot
        - Removed angles definition from dictionnary and replaced with fixed angles
        - Added translation keyword, also reported in ias_gse.point_source_to_fov_translation

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
def cam_tvpt_040_straylight(cam_num_frames=None, theta=None, phi=None, translation=[-80, 80], fwc_fraction=None, fwc_factor=None):
    """
    SYNOPSIS
    cam_tvpt_040(cam_num_frames=15,ooF_objective='oof_moon',fwc_factor=0.7)
    cam_num_frames_sat : number of frames per FoV position; same for background acquisition
    ooF_objective : target definition for SRON 'ooF_moon','ooF_edge1','ooF_edge2','ooF_edge3'
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
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_moon',fwc_factor=0.7) # 15 * 25s (full_standard) * 4 azimuths * 3 executions = 75min  (3execution bkg and straylight and saturated)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_edge1',fwc_factor=0.7) #  = 50min (2execution bkg and straylight)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_edge2',fwc_factor=0.7) #  = 50min (2execution bkg and straylight)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_edge3',fwc_factor=0.7) #  = 50min (2execution bkg and straylight)
    For IAS
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_moon',fwc_factor=0.7)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_edge1',fwc_factor=0.7)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_edge2',fwc_factor=0.7)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_edge3',fwc_factor=0.7)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_edge4',fwc_factor=0.7)
    $ execute(cam_tvpt_040_straylight,cam_num_frames=15,ooF_objective='oof_IAS_max',fwc_factor=0.7)
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
    # The dict includes per objective:
    #           1) the FWC for set_attenuation, float
    #           2) the theta angles for point_source_to_fov_translation, float
    #           3) the phi angles for point_source_to_fov_translation, list of float for loop

    # ## measurements at 0, 90deg and 18.88deg will be performed with different intensities within the Ghost test
    # ## measurements at 45deg and TBD are supposed to be done within the vignetting test
    # ## moved start of the OoF measurements to start at 19deg
    # ## kept the angles at 0, 45, 90 deg for the PST
    # ## added angle at 5deg for Flexi
    # ## 65deg optional for F-CAMs and vignetting test overlap (IAS only)
    oof_phi_angles = [0., 5., 45., 90.]
    oof_phi_ias_angles = [0., 5., 45., 65., 90.]

    oof_objective_dict = {'oof_moon': [fwc_factor, 20., oof_phi_angles],
                          'oof_edge1': [fwc_factor, 19.63, oof_phi_angles],
                          'oof_edge2': [fwc_factor, 19.33, oof_phi_angles],
                          'oof_edge3': [fwc_factor, 19.0, oof_phi_angles],
                          'oof_IAS_max': [fwc_factor, 23., oof_phi_ias_angles],
                          'oof_IAS_edge4': [fwc_factor, 21., oof_phi_ias_angles],
                          'oof_IAS_moon': [fwc_factor, 20., oof_phi_ias_angles],
                          'oof_IAS_edge1': [fwc_factor, 19.63, oof_phi_ias_angles],
                          'oof_IAS_edge2': [fwc_factor, 19.33, oof_phi_ias_angles],
                          'oof_IAS_edge3': [fwc_factor, 19.0, oof_phi_ias_angles],
                          }

    # D. COMMANDING
    # Idea gimbal sites illuminate more the +XPLM side, hexapod does all
    for vertical in translation:
        ogse.set_fwc_fraction(fwc_fraction=fwc_fraction)

        LOGGER.info(f"CAM-TVPT-040 Pointing source to field position in Tz ({vertical}, {theta})")
        # MGSE move
        # wait = True is that BIG, SMALL, and Translation stage in position
        mgse.point_source_to_fov_translation(theta=theta, phi=phi, translation_z=vertical, wait=True)
        visit_field_angles(theta, phi)

        # Dark measurement
        LOGGER.info(f"CAM-TVPT-040 Starting Dark Measurement")
        # TODO F-CAM
        dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=cam_num_frames, ccd_side="BOTH")

        # Straylight measurement
        LOGGER.info(f"CAM-TVPT-040 Starting Straylight Measurement")
        ogse.shutter_open()
        dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=cam_num_frames, ccd_side="BOTH")
        ogse.shutter_close()

    LOGGER.info(f"CAM-TVPT-040 Finish")

    system_to_idle()  # FEE in dump, OGSE shutter close, filter unknown TCS on, MGSE ready Sec. 14