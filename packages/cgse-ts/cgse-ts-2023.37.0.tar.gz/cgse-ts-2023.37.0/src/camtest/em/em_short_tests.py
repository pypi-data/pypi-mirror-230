import logging

import time

import numpy as np
from numpy.random import uniform

from camtest import building_block
from camtest.commanding import dpu
from camtest.commanding.dpu import wait_cycles
from camtest.commanding.mgse import point_source_to_fov
from egse.hk import get_housekeeping

LOGGER = logging.getLogger(__name__)


@building_block
def short_sync_test(num_subpix=None, num_frames=None, num_bck=None, fov_coordinates=None, dith_amp=None):
    """
    SYNOPSIS
    cam_tvpt_010(temperature, num_subpix=25, num_frames=1, num_bck=2)

    Acquisition for 5 TRP1 temperatures of
        - 40 FoV positions
        - in each FoV position num_subpix sub-pixels positions
        - in each sub-pixel positions a total of num_frames images

    EXAMPLE
    $ execute(cam_tvpt_010,temperature=-80, num_subpix=25,num_frames=1, num_bck=1)

    """
    ccd = 3
    ccd_rot = {4: 0, 1: 90, 2: -180, 3: -90}  # this defines the angles to sum to fov_coordinates for each ccd

    # A. CHECK STARTING CONDITIONS

    # if systen not idle -> Abort is raised
    #system_test_if_idle()

    # B. DEFINITION TEST PARAMETERS

    #fov_coordinates = [[3.1, 45], [8.3, 24.40]]

    # these coordinates correspond to all 10 points on ccd4

    #dith_amp = 0.004  # 0.002 is ~half a pixel size in deg


    # C. COMMANDING

    for position in fov_coordinates:
        # visit each angle coordinate

        # Point CAM to first FoV position
        theta0 = position[0]
        phi0 = position[1]

        LOGGER.info(f"Pointing source to field angles ({theta0}, {phi0})")
        point_source_to_fov(theta=theta0, phi=phi0, wait=True)

        # Acquire background images:
        n_fee_parameters = dict(
            num_cycles=num_bck,
            row_start=4000,
            row_end=4509,
            rows_final_dump=4510,
            ccd_order=[3, 3, 3, 3],
            ccd_side="E",
            exposure_time=0.2
        )
        dpu.n_cam_partial_int_sync(**n_fee_parameters)

        # Acquire dithered images -> infinite loop:
        n_fee_parameters["num_cycles"] = 0
        dpu.n_cam_partial_int_sync(**n_fee_parameters)

        for subpix in range(num_subpix):
            # num_subpix random positions around these x,y coordinates

            wait_cycles(num_frames - 1)
            theta = theta0 + uniform(-dith_amp, dith_amp)
            phi = phi0 + uniform(-dith_amp, dith_amp)
            dpu.on_long_pulse_do(point_source_to_fov, theta=theta, phi=phi, wait=False)

        wait_cycles(num_frames)

        dpu.n_cam_to_dump_mode()

    #system_to_idle()


@building_block
def validate_gethk(theta=None, phis=None, tolerance=None, time_granularity=None):
    """
    Validate get_housekeeping
    """

    time.sleep(5.)

    for phi in phis:
        LOGGER.info(f"Phi: {phi}")

        point_source_to_fov(theta=theta, phi = phi, wait = False)

        LOGGER.info("Moved -> get HK")

        _, phi_meas = get_housekeeping(device="SMC", hk_name="axis 1 - cur_pos")

        while np.abs(float(phi_meas)-phi) > tolerance:

            LOGGER.info(f"{phi_meas}, {phi}, {float(phi_meas) - phi}")

            time.sleep(time_granularity)

            _, phi_meas = get_housekeeping(device="SMC", hk_name="axis 1 - cur_pos")
