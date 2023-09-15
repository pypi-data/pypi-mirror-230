"""
PLATO TVAC TEST CAMPAIN
HIGH LEVEL TEST SCRIPT FOR TEST
CAM-TVPT-060 Camera long-term stability
N-CAM
Start condition:
    Dark conditions in the lab, see test specification & test procedure
    Shutter closed
    CAM in DUMP mode
End status
    Shutter closed
    CAM in DUMP mode
Authors: M. Pertenais, C. Paproth, A. Börner, P. Guiot
Versions:
    2022 03 28 - 0.1 Draft -- Creation
    2022 05 09 - 0.2 Draft -- Modification after review from KUL and IAS
    2022 07 25 - 1.0 First release version -- Modification with slicing and shutter opening
"""

import logging
from time import sleep

import numpy as np

from camtest import building_block
from camtest.commanding import dpu, ogse, system_to_idle, system_test_if_idle
from camtest.commanding.mgse import point_source_to_fov
from egse.state import GlobalState
from egse.visitedpositions import visit_field_angles

LOGGER = logging.getLogger(__name__)


@building_block
def cam_tvpt_060(time=None, num_bck=None, fwc_fraction=None, theta=None, phi=None, cycles_per_fits=None, delay=1000,
                 integration=15000):
    """
    SYNOPSIS
    cam_tvpt_060(time=None, num_bck=None, fwc_fraction=None, theta=None, phi=None,  cycles_per_fits=None)
    Acquisition for at the nominal TRP1 temperature of the image of the special mask
    with 4 small pinholes and a larger one.
    time = in hours the approximate time wanted of measured signal
    num_back= number of background images acquired before the shutter is opened
    fwc_fraction = TBD by IAS setup, ~50% of FWC
    theta, phi = angles in deg of the FoV
    cycles_per_fits = number of frames per fits file

    EXAMPLES
    $ execute(cam_tvpt_060(time=1, num_bck=0, fwc_fraction=0.00005, theta=2, phi=45,  cycles_per_fits=100))
    $ execute(cam_tvpt_060(time=44, num_bck=5, fwc_fraction=0.00005, theta=2, phi=45 cycles_per_fits=100))
    """

    # A. CHECK STARTING CONDITIONS

    system_test_if_idle()
    setup = GlobalState.setup

    def shutter_sync(delay=delay, integration=integration):
        shutter = setup.gse.shutter.device
        shutter.set_mode('auto')
        shutter.set_cycle(integration, delay, 1)
        sleep(5)
        shutter.set_enable(1)


    # B. DEFINITION TEST PARAMETERS
    ogse.set_fwc_fraction(fwc_fraction=fwc_fraction) #could be removed, and commanded separately before the test

    # C. COMMANDING
    # Point CAM to first FoV position

    number_cycles = np.ceil(time * 3600 / 25)  # time in hours, 1 cycle every 25s
    num_fits = np.ceil(number_cycles / cycles_per_fits)  # example for time=1h, number_cycles=144, num_fits = 2 (100 cycles in 1st fit, 44 on the 2nd)


    LOGGER.info(f"Pointing source to field angles ({theta}, {phi})")
    point_source_to_fov(theta=theta, phi=phi, wait=True)
    visit_field_angles(theta, phi)

    # Acquire background images:
    LOGGER.info(f"Acquiring Background frames for the FoV position ({theta}, {phi})")
    dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=num_bck, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                           rows_overscan=30)

    LOGGER.info(f"Acquiring Images for the FoV position ({theta}, {phi})")

    # Specify fits-slicing parameter
    dpu.set_slicing(num_cycles=cycles_per_fits)

    # Start infinite loop of acquisition
    LOGGER.info(f"Starting acquisition cycle")
    dpu.on_frame_number_do(3, dpu.n_cam_full_ccd, num_cycles=0, ccd_order=[1, 2, 3, 4], ccd_side="BOTH",
                           rows_overscan=30)

    for cycle in range(int(number_cycles)):
        dpu.on_long_pulse_do(shutter_sync, delay=delay, integration=integration)
        LOGGER.info(f"Acquisition cycle in progress at {cycle} in {int(number_cycles)}")

    # Put the setup back to idle (incl. reset of fits slicing), ready for the next test
    system_to_idle()
