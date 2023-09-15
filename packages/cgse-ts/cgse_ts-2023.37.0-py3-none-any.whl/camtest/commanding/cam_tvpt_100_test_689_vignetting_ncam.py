"""
PLATO TVAC TEST CAMPAIGN
PLATO-KUL-PL-TS-0001 CAM-TVPT-100 Vignetting
EM N1-CAM

Requirements:
- PLT-CAM-1931
- PLT-CAM-1513

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    system in idle mode
End status
    system in idle mode
Synopsis:
    - TRP1 temperature is at nominal temperature after Best Focus Scan
    - Nominal thermal stabilization criteria achieved
    - visit all FoV positions
        - acquire bkg
        - open shutter
        - Set OGSE intensity to TBD values
        - Acquire TBD images
        - close shutter
Authors: lead by TBD
Versions:
    2021 10 21 - 0.1 Draft -- Proposal creation copy paste from best focus scan by TK to discuss overlap with CAM TVPT 040

"""
import logging

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.mgse import point_source_to_fov
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_100(num_frames=None, num_bck=None, fwc_factor=None):
    """
    SYNOPSIS
    cam_tvpt_100(num_frames=2, num_bck=2,fwc_factor=0.4)
        - max 10 FoV positions in 4 places around the FOV edge as indicated in CAM TS Spec
        - at least 1 FOV postion close to the center

        FWC factor
        # max 17kADU with worst case 25e-/ADU gain -> 425ke
        # kept same as for Best Focus Scan; CAM TS spec mentions 500ke

    $ execute(cam_tvpt_100,num_frames=2, num_bck=2)
    """
    # A. CHECK STARTING CONDITIONS

    system_test_if_idle()  # if systen not idle -> Abort is raised

    # B. DEFINITION TEST PARAMETERS
    ogse.set_fwc_fraction(fwc_fraction=fwc_factor)

    # the positions [3.1,45],[12.4,45] would be given by ghost test
    # off axis angles selected PLATO-LDO-PL-RP-0002 Issue 4, Sec. 4.5.2
    fov_coordinates = [[1, 45], [7, 45], [14, 45], [16.0, 45], [16.5, 45], [17.0, 45], [17.5, 45], [18.0, 45],
                       [18.5, 45], [18.88, 45]]
    # these coordinates correspond to all 8 points on a ccd

    ccd_rot = {4: 0, 1: 90, 2: -180, 3: -90}  # this defines the angles to sum to fov_coordinates for each ccd

    LOGGER.info(f"cam_tvpt_100 Start")

    # C. COMMANDING
    for ccd in [4, 1, 2, 3]:
        # these 2 loops can be interchanged if quicker to move the gimbal across CCDs
        ccdorder = {1: [1, 2, 3, 4], 2: [2, 3, 4, 1],
                    3: [3, 4, 2, 1], 4: [4, 1, 2, 3]}

        for position in fov_coordinates:
            # visit each angle coordinate within ccd number ccd

            # Point CAM to first FoV position
            theta0 = position[0]
            phi0 = position[1] + ccd_rot[ccd]

            LOGGER.info(f"cam_tvpt_100 Pointing source to field angles ({theta0}, {phi0})")
            point_source_to_fov(theta=theta0, phi=phi0, wait=True)
            visit_field_angles(theta0, phi0)

            # TBC Open point - read all CCDs (additional data) or only the CCD for the Vignetting/illuminated
            # Acquire background images:
            LOGGER.info(f"cam_tvpt_100 Acquiring Background frames for the FoV position ({theta0}, {phi0})")
            dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_bck, ccd_order=ccdorder[ccd], ccd_side="BOTH",
                                   rows_overscan=0)

            # Start infinite loop of acquisition
            LOGGER.info(f"cam_tvpt_100 Acquiring Images for the FoV position ({theta0}, {phi0})")
            ogse.shutter_open()
            dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_frames, ccd_order=ccdorder[ccd],
                                   ccd_side="BOTH", rows_overscan=0)

            # close shutter and stop acquiring images before moving to next FoV position:
            ogse.shutter_close()
            # dump mode needed here?
            dpu.on_frame_number_do(3, dpu.n_cam_to_dump_mode)

    LOGGER.info(f"cam_tvpt_100 Finish")
    # Put the setup back to idle, ready for the next test
    system_to_idle()
