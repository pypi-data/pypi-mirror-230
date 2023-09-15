"""
Demo scripts for the EM test scripts rehearsal of the week of June 14th, 2021.
"""
import logging

from camtest.commanding import system_test_if_idle, system_to_idle, dpu
from camtest.commanding.dpu import on_long_pulse_do, wait_cycles
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from camtest.commanding.mgse import point_source_to_fov
from camtest.core.exec import building_block
from egse.state import GlobalState
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def demo_basic(fov_angles, num_cycles=None, ccd_side=None):
    """ Basic demo script.

    The goal of this demo script is to show:

        - how to check whether the EGSE system is in the correct state at the start of the script (idle);
        - how to get access to the setup that has been loaded (it should not be loaded in the test script, but be
          accessed from the GlobalState);
        - how to get hold of information in the setup;
        - how to put a point source at the given location (only implemented for CSL at this point);
        - how to acquire images;
        - how to bring the EGSE system back in a state it is ready for the next test (idle).

    Args:
        - fov_angles: Field angles (theta, phi) at which to put the source.
        - nfee_parameter: Parameters to configure the N-FEE.
    """

    # Check if the EGSE system is in the correct state to start a test
    # (will abort if not)

    system_test_if_idle()

    # Access the setup that has been loaded

    setup = GlobalState.setup

    # Get hold of information in the setup

    site = setup.site_id
    LOGGER.info(f"Executing basic demo for {site}")

    # Point the source at a given location

    theta, phi = fov_angles
    LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
    point_source_to_fov(theta=theta, phi=phi, wait=True)
    visit_field_angles(theta, phi)

    # Acquire images

    LOGGER.info("Starting integration")
    # dpu.n_cam_full_standard(num_cycles=num_cycles, ccd_side=ccd_side)
    nfee_parameters = {}
    nfee_parameters["num_cycles"] = num_cycles                       # ∞ loop!
    nfee_parameters["row_start"] = 1000
    nfee_parameters["row_end"] = 1200
    nfee_parameters["rows_final_dump"] = 0
    nfee_parameters["ccd_order"] = [1, 2, 3, 4]
    nfee_parameters["ccd_side"] = ccd_side
    # dpu.n_cam_partial_ccd(num_cycles=None, row_start=None, row_end=None,
    #                   rows_final_dump=None, ccd_order=None, ccd_side=None)

    dpu.n_cam_partial_ccd(**nfee_parameters)      # ∞ loop!

    # Bring the system in a state that it is ready for the next test

    system_to_idle()


@building_block
def demo_sync_readout(fov_angles,num_cycles=5,rows_final_dump=0, roi_width=200):
    """ Demo script to demonstrate the synchronisation of the mechanisms.

    The goal of this demo script is to show:
    - How to compute the (distorted) CCD coordinates corresponding to given FoV angles [boresight angle, azimuth]
    - How to configure partial CCD readout
    - How to synchronize one CCD readout with the rest of the test-environment (e.g. MGSE mechanisms)

    Args:
        - fov_angles:
    """

    # Check if the EGSE system is in the correct state to start a test
    # (will abort if not)

    system_test_if_idle()

    num_positions = fov_angles.shape[0]

    ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(fov_angles, distorted=True, verbose=True)

    nfee_parameters = {}
    nfee_parameters["num_cycles"] = 0                       # ∞ loop!
    nfee_parameters["row_start"] = int(ccdrows[0]-roi_width//2)
    nfee_parameters["row_end"] = int(ccdrows[0]+roi_width//2)
    nfee_parameters["rows_final_dump"] = rows_final_dump
    nfee_parameters["ccd_order"] = [ccdcodes[0],ccdcodes[0],ccdcodes[0],ccdcodes[0]]
    nfee_parameters["ccd_side"] = ccdsides[0]
    # dpu.n_cam_partial_ccd(num_cycles=None, row_start=None, row_end=None,
    #                   rows_final_dump=None, ccd_order=None, ccd_side=None)

    dpu.n_cam_partial_ccd(**nfee_parameters)      # ∞ loop!

    on_long_pulse_do(point_source_to_fov, theta=fov_angles[0, 0], phi=fov_angles[0, 1], wait=True)
    visit_field_angles(fov_angles[0, 0], fov_angles[0, 1])

    LOGGER.info(f"MGSE in Position 0")

    for pos in range(1, num_positions):

        # Acquire the desired nb of images - 1
        wait_cycles(num_cycles-1)

        # Acquire last image & dither move at next pulse
        on_long_pulse_do(point_source_to_fov, theta=fov_angles[pos, 0], phi=fov_angles[pos, 1], wait=False)
        visit_field_angles(fov_angles[pos, 0], fov_angles[pos, 1])

        LOGGER.info(f"{pos=}")

    # Acquire the images in the last commanded position
    wait_cycles(num_cycles)

    # Bring the system in a state that it is ready for the next test
    on_long_pulse_do(system_to_idle)
