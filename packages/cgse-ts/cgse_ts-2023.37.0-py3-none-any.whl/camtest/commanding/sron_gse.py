""" SRON-specific GSE:  Commanding the mechanisms at SRON """
import logging
from time import sleep
import numpy as np

from camtest.core.exec import building_block
from egse import coordinates
from egse.settings import Settings
from egse.stages.aerotech.ensemble_interface import EnsembleInterface
from egse.state import GlobalState
from egse.control import Failure
from egse.exceptions import Abort

logger = logging.getLogger(__name__)

FOV_SETTINGS = Settings.load("Field-Of-View")


@building_block
def sron_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at SRON such that the illuminated position is at the given angular distance from the
    optical axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - wait: Whether or not to wait for the stages to reach the commanded positions.
    """

    ensemble: EnsembleInterface = GlobalState.setup.gse.ensemble.device

    phi = 180. - phi
    if phi > 180.:
        phi -= 360.

    # Transform angles according to "PLATO CAM TVAC Gimbal Characterization Report" by Robert
    theta, phi = np.deg2rad(theta), np.deg2rad(phi)
    angle_x = np.rad2deg(np.arcsin(-np.sin(phi + np.pi) * np.sin(theta)))
    angle_y = np.rad2deg(np.arctan(np.cos(phi + np.pi) * np.tan(theta)))

    #angle_x = degrees(asin(-sin(radians(phi) + pi) * sin(radians(theta))))
    #angle_y = degrees(atan2(cos(radians(phi) + pi) * tan(radians(theta))))

    # Command the gimbal (avoid checking limits in software)
    response = ensemble.move_axes_degrees(position_x=angle_x, position_y=angle_y)

    if isinstance(response, Failure):
        raise Abort(response)

    if wait:
        # While any gimbal axis is moving : wait
        # See issue #418: test "while not 'in-position'" occasionally never exits
        while bool(ensemble.get_plane_status() & 0x1):
            sleep(5)
        # Additional sleep is necessary to make sure the gimbal is actually in place
        sleep(20)


@building_block
def sron_point_source_to_fov_translation(theta=None, phi=None, translation_z=None, wait=True):

    raise NotImplementedError


@building_block
def sron_point_source_to_fp(x=None, y=None, wait=None) -> (float, float):
    """ Position source on (x,y).

    Position the EGSE mechanisms at SRON such that the illuminated position is at the given focal-plane coordinates.

    Args:
        - x: Focal-plane x-coordinate to move to [mm].
        - y: Focal-plane y-coordinate to move to [mm].
        - wait: Whether or not to wait for the mechanisms to reach the commanded positions.

    Returns:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
    """

    x_undistorted, y_undistorted = coordinates.undistorted_to_distorted_focal_plane_coordinates(
        x, y, FOV_SETTINGS.DISTORTION_COEFFICIENTS, focal_length=FOV_SETTINGS.FOCAL_LENGTH
    )

    theta, phi = coordinates.focal_plane_coordinates_to_angles(x_undistorted, y_undistorted)
    sron_point_source_to_fov(theta=theta, phi=phi, wait=wait)

    return theta, phi


def sron_enable():
    """ Enable control of the camera rotation mechanism for pointing, for SRON.

    This function should never be called from a test script.  Instead, call the generic function enable().
    """
    ensemble: EnsembleInterface = GlobalState.setup.gse.ensemble.device

    ensemble.enable_axes()

    ensemble.clear_errors()
    
    ensemble.home_axes()
    
    response = ensemble.move_axes_degrees(position_x=0, position_y=0)

    if isinstance(response, Failure):
        raise Abort(response)


def sron_disable():
    """ Move the camera rotation mechanism to the equilibrium position and release the controller, for SRON.

    When pointing is not needed (e.g during warm up phases), the camera rotation mechanisms is moved to the
    equilibrium position and the controller is released.

    This function should never be called from a test script.  Instead, call the generic function disable().
    """

    setup = GlobalState.setup

    ensemble: EnsembleInterface = setup.gse.ensemble.device
    ensembleRestingPositions = setup.gse.ensemble.resting_positions

    if bool(ensemble.get_status('X') & 0x1) and bool(ensemble.get_status('Y') & 0x1):
        # Move gimbal to a save position to prevent the camera from falling
        response = ensemble.move_axes_degrees(ensembleRestingPositions.X, ensembleRestingPositions.Y)

        if isinstance(response, Failure):
            raise Abort(response)

        while bool(ensemble.get_plane_status() & 0x01):
            sleep(5)

        # Disable the gimbal when it has reached the save position
        ensemble.disable_axes()
    else:
        logger.info("Gimbal has already been disabled")
