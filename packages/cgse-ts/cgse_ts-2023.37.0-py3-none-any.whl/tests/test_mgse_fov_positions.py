import logging
import time

import numpy as np
import pytest

from camtest import start_observation, end_observation
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from camtest.commanding.mgse import point_source_to_fov, enable, disable
from egse.setup import load_setup
from egse.stages.huber.smc9300 import HuberSMC9300Proxy

LOGGER = logging.getLogger("camtest.tests.huber")


@pytest.mark.parametrize("fov_table", ["reference_full_40", "reference_single", "reference_circle_20"])
def test_reference_positions(fov_table):
    """
    The purpose of this test is to execute the FOV positions without interactions with the camera.
    No attempt will be done to read out the Camera. The test is parametrized for the FOV table name
    that is selected from the Setup. All fov_positions will be visited.

    Prerequisites:

        * core egse services must be running
        * a proper Setup must be loaded in the cm_cs

    Note:

        This test is based on the best focus determination script: TVPT_010.
    """
    # I use warning level here to emphasize the log message
    LOGGER.warning(f"FOV Position test started for {fov_table}...")

    setup = load_setup()

    LOGGER.info(f"Loaded Setup {setup.get_id()} for this test.")
    use_angles = True
    verbose = True

    start_observation(f"MGSE Test for FOV positions: {fov_table}")

    # fov_coordinates: Tuple[float,float] of theta and phi

    enable()

    ccdrows, ccdcols, ccdcodes, ccdsides, fov_coordinates = fov_geometry_from_table(
        distorted=True, distorted_input=False, table_name=fov_table, use_angles=use_angles, verbose=verbose)

    fov_selection = np.arange(len(ccdrows))
    npos = len(fov_selection)

    for pos_nr, (posid, position) in enumerate(zip(fov_selection, fov_coordinates[fov_selection])):

        if ccdrows[posid] is None or ccdcols[posid] is None or ccdcodes[posid] is None or ccdsides[posid] is None:
            LOGGER.warning(f"Invalid Selected Field Positions:\n {fov_coordinates[fov_selection]}")
            continue

        theta = position[0]
        phi = position[1]

        LOGGER.info(f"pos {posid}  (pos {pos_nr:2d}/{npos}). Pointing source to field angles  [{theta}, {phi}]")

        point_source_to_fov(theta=theta, phi=phi, wait=True)

    disable()

    end_observation()


def test_sign_problem_big_rotation_stage():
    """
    This test moves the big rotation stage to several positions within the range [-160, -180].
    """

    with HuberSMC9300Proxy() as huber:

        for angle in [-160, -162, -164, -166, -168, -170, -172, -174, -176, -178,
                      -180, -182, -184, -186, -188, -190, -192, -194, -196, -200]:
            try:
                huber.goto(axis=1, position=angle, wait=True)
            except ValueError as exc:
                LOGGER.error(f"Caught ValueError: {exc}")
            LOGGER.info(f"{huber.get_current_position(axis=1) = }")
            time.sleep(1.0)

        for angle in [160, 162, 164, 166, 168, 170, 172, 174, 176, 178,
                      180, 182, 184, 186, 188, 190, 192, 194, 196, 198, 200]:
            try:
                huber.goto(axis=1, position=angle, wait=True)
            except ValueError as exc:
                LOGGER.error(f"Caught ValueError: {exc}")
            LOGGER.info(f"{huber.get_current_position(axis=1) = }")
            time.sleep(1.0)
