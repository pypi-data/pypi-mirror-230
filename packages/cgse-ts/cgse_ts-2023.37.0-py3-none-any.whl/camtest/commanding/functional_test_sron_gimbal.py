"""
PLATO TVAC TEST CAMPAIN

HIGH LEVEL TEST SCRIPT FOR HARTMANN VERIFICATION TEST AT AMBIENT, OVER A SET OF POSITIONS AT A FIXED BORESIGHT ANGLE

N-CAM

Start condition:
    Dark conditions in the lab, see test specification & test procedure
    CAM in DUMP mode or DUMP mode internal sync

End status
    CAM in DUMP mode internal sync
    MGSE with the source at the last visited FoV position

Synopsis:

Authors: P. Royer

Versions:
    2020 10 27 : Creation from cam_aat_050_ambient_hartmann_recentering_prep [ran multiple times in CSL at EM level]


"""
import logging

from egse.exceptions import Abort
import numpy as np
from camtest.commanding.functions.sron_functions import fov_angles_to_gimbal_rotations
from camtest.commanding import mgse
from egse.hk import get_housekeeping
from camtest import building_block

LOGGER = logging.getLogger(__name__)


@building_block
def functional_test_sron_gimbal_fov_angles(thetas=None, phis=None, tolerance=None):
    """

    """
    if thetas is None or phis is None:
        LOGGER.info("thetas or phis == None ==> using defaults")

        thetas = np.array([3.1, 8.3, 12.4, 16.33])
        phis = np.array([-167., 45., -45, 120.])

    npos = len(thetas)
    c = -1

    for theta, phi in zip(thetas, phis):
        c += 1

        rx, ry = fov_angles_to_gimbal_rotations(theta, phi)

        mgse.point_source_to_fov(theta=theta, phi=phi, wait=True)

        tsx, xpos = get_housekeeping("GSRON_ENSEMBLE_ACT_POS_X")
        tsy, ypos = get_housekeeping("GSRON_ENSEMBLE_ACT_POS_Y")

        diffx, diffy = xpos - rx, ypos - ry
        LOGGER.info(
            f"Move {c}/{npos}: Commanded vs Current Pos X [{rx},{xpos}] Y [{ry},{ypos}]  Diffs [{diffx},{diffy}]")

        if not (abs(diffx) <= tolerance) or not (abs(diffy) <= tolerance):
            raise Abort(f"Current [{xpos},{ypos}] & commanded positions [{rx},{ry}] not within tolerance {tolerance}")
