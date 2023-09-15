"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR TEST

6.9.8 CAM-TVPT-090 Ghosts Characterization

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    CAM in dump mode

End status
    CAM in dump mode

Synopsis:
    - visit all FoV positions
        acquire background images
        open shutter
        Set OGSE intensiry to required values
        Acquire TBD images
        close shutter

Authors: M. Pertenais

Versions:
    2020 09 09 - 0.1 Draft -- Creation
    2021 03 23 - 0.2 Draft -- Update after several meetings :
            (addition of background, removal of several intensities and update of acquisition mode to full frame)
    2021 09 16 - 0.3 Draft -- Preparation for TRR, addition of manual visit option
    2021 11 03 - 0.4 Draft -- proposed version for the EM test at SRON
    2021 11 03 - 1.0 -- version used at SRON on the EM (equal to v0.4)
    2022 07 15 - 1.1 -- proposed version for the EM test at IAS
    2023 03 14 - 1.2 -- proposed version for the PFM test at IAS

"""
import logging

from camtest import building_block
from camtest.commanding import dpu, system_test_if_idle, system_to_idle
from camtest.commanding import ogse
from camtest.commanding.mgse import point_source_to_fov
from egse.exceptions import Abort
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_090(num_frames_sat=None, num_frames_nonsat=None, num_bck=None,
                        fwc_sat=None, fwc_nonsat=None, manual_visit=None,
                        angles_manual=None, fwc_manual=None, num_frames_manual=None):
    """
    SYNOPSIS
    cam_tvpt_090(num_frames_sat=3, num_frames_nonsat=3, num_bck=3, fwc_sat=1000,
                 fwc_nonsat=0.75, manual_visit=False, angles_manual=[[0,0]],
                 fwc_manual=1, num_frames_manual=3)

    num_frames_sat : number of frames per FoV position for the saturated illumination
    num_frames_nonsat : number of frames per FoV position for the non-saturated illumination
    num_bck : number of background frames per FoV position
    manual_visit : to use only to manually visit a position
    fwc_manual, num_frames_manual: used only in the manual mode

    EXAMPLES

    $ execute(cam_tvpt_090, num_frames_sat=3, num_frames_nonsat=3, num_bck=3,
              fwc_sat=1000, fwc_nonsat=0.75, manual_visit=False,
              angles_manual=[[0,0]], fwc_manual=1, num_frames_manual=3)
    """

    # A. CHECK STARTING CONDITIONS
    #       - system not idle -> Abort is raised
    #       - assumed is that TRP1 is already set (we just need to check that the temperature is stable)

    system_test_if_idle()

    if not manual_visit == True and not manual_visit == False:
        raise Abort("The manual_visit parameter is not known. It shall be exclusively: True or False")

    # B. DEFINITION TEST PARAMETERS

    #theta_array_SRON = [3.8, 7.6, 11.4, 15.2, 18.88]        # theta = angle from the optical axis
    #phi_array_SRON = [0, 30, 60, 90, 135, 225, 315]
       
    phi_array = [45, 135, 225, 315]
    theta_array = [1.0, 3.8, 5.4, 7.0, 8.0, 9.2, 11.4, 13.0, 15.2]
    theta_array_nonsat = [1.0, 3.8, 5.4, 7.0, 8.0, 9.2, 11.4, 13.0, 15.2]

    num_frames = {"sat":num_frames_sat, "nonsat":num_frames_nonsat, "manual":num_frames_manual}

    # C. COMMANDING

    ### This part happens only in case the operator manually wants to visit a position ###
    if  manual_visit == True:
        for angle in angles_manual:
            theta = angle[0]
            phi = angle[1]

            LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
            point_source_to_fov(theta=theta, phi=phi, wait=True)
            visit_field_angles(theta, phi)

            # Acquire the background images (both CCD sides)
            LOGGER.info("Acquiring Background images")
            dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_bck, ccd_side="BOTH")
            ogse.shutter_open()

            # Acquire the ghost images (both CCD sides)
            LOGGER.info("Acquiring images")
            ogse.set_fwc_fraction(fwc_fraction = fwc_manual)
            dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_frames["manual"], ccd_side="BOTH")
            ogse.shutter_close()

    ### This part is the nominal automatic script
    if manual_visit == False:
        for phi in phi_array:                   # visit all azimuths
            for theta in theta_array:           # visit all angular radii

                LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
                point_source_to_fov(theta=theta, phi=phi, wait=True)
                visit_field_angles(theta, phi)

                # Acquire the background images (both CCD sides)
                LOGGER.info("Acquiring Background images")
                # do I need something here to clear out the CCDs? Especially if the previous acquisition was highly saturated...
                dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_bck, ccd_side="BOTH")
                ogse.shutter_open()

                # Acquire the ghost images (both CCD sides)
                
                if theta in theta_array_nonsat:
                    LOGGER.info("Acquiring non-saturated images")
                    ogse.set_fwc_fraction(fwc_fraction=fwc_nonsat)
                    dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_frames["nonsat"], ccd_side="BOTH")

                LOGGER.info("Acquiring saturated images")
                ogse.set_fwc_fraction(fwc_fraction=fwc_sat)
                dpu.on_frame_number_do(3, dpu.n_cam_full_standard, num_cycles=num_frames["sat"], ccd_side="BOTH")
                ogse.shutter_close()

    system_to_idle()
