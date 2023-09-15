"""
INTA-specific GSE:  Commanding the mechanisms at INTA

TODO To be implemented by INTA.
"""

from camtest.core.exec import building_block
from egse.state import GlobalState
from egse import coordinates
import time
import numpy as np
import logging
from egse.settings import Settings
from egse.exceptions import Abort

################################################################################
### COMMANDING THE GIMBAL
################################################################################

#### BB TO MOVE THE GIMBAL
@building_block
def gimbal_move_absolute(
    grx=None,
    gry=None,
    wait=None,
):

    """ Move the Gimbal in user coordinates, absolute sense

    Move the Gimbal to the given angular position. The
    absolute movement is expressed in the user coordinate system.

    Args:
        - grx (float): rotation around the X-axis [deg]
        - gry (float): rotation around the Y-axis [deg]
        - wait: Whether or not to wait for the gimbal to reach its commanded positions.

    """

    setup = GlobalState.setup

    gimbal = setup.gse.gimbal.device
    granularity = setup.gse.gimbal.time_request_granularity

    gimbal.move_absolute(grx, gry)

    if wait:
        while not is_gimbal_in_position():
            time.sleep(granularity)

@building_block
def gimbal_goto_zero_position(wait=None):
    """ Move the gimbal to the zero position.

    Args:
        - wait: boolean - Whether or not to wait for the gimbal to reach its retracted
                position.
    """

    setup = GlobalState.setup

    gimbal = setup.gse.gimbal.device
    granularity = setup.gse.gimbal.time_request_granularity

    gimbal.goto_zero_position()

    # Wait for the gimbal to reach the zero position
    if wait:
        while not is_gimbal_in_position():
            time.sleep(granularity)


#### BB TO CHECK THE gimbal STATUS

@building_block
def gimbal_request_user_positions():
    """Returns the user positions of the gimbal as an array of floats.

    Returns: [GRx, GRy].
        GRx: rotation around the X-axis [deg]
        GRy: rotation around the Y-axis [deg]
    """
    gimbal = GlobalState.setup.gse.gimbal.device

    return gimbal.get_user_positions()


def gimbal_check_absolute_movement(
    grx=None,
    gry=None
):

    """ Checks if the requested absolute movement is valid.

    Checks the gimbal to the given position and orientation. The
    absolute movement is expressed in the user coordinate system.

    Args:
        - grx (float): rotation around the X-axis [deg]
        - gry (float): rotation around the Y-axis [deg]

    """

    gimbal = GlobalState.setup.gse.gimbal.device
    return gimbal.check_absolute_movement(grx, gry)

@building_block
def gimbal_configure_offsets():

    """ Configure the User Coordinate System taken from the setup file.
    """

    gimbal = GlobalState.setup.gse.gimbal.device


    if 'offsets' in GlobalState.setup.gse.gimbal:
        gimbal_off = GlobalState.setup.gse.gimbal.offsets
    else:
        gimbal_off = [0., 0.]

    return gimbal.configure_offsets(*gimbal_off)

@building_block
def gimbal_reset_offsets():

    """ Make sure the offsets are null, so (0, 0) actually refers to a hori-
    zontally-oriented Gimbal.
    """

    gimbal = GlobalState.setup.gse.gimbal.device

    return gimbal.configure_offsets(0, 0)


@building_block
def is_gimbal_in_position():
    """ Checks whether the gimbal is in position and not moving.

    Returns:
        - True if the gimbal is in position and not moving; False otherwise.
    """

    gimbal = GlobalState.setup.gse.gimbal.device

    return gimbal.is_in_position()

@building_block
def gimbal_clear_error():
    """
    Clear all errors in the controller software.
    """
    gimbal = GlobalState.setup.gse.gimbal.device

    gimbal.clear_error()

@building_block
def gimbal_activate_control_loop():
    """
    Activate the Gimbal's control loop, needed to command movements.
    """
    gimbal = GlobalState.setup.gse.gimbal.device

    gimbal.activate_control_loop()

@building_block
def gimbal_deactivate_control_loop():
    """
    Deactivate Gimbal's control loop.
    """
    gimbal = GlobalState.setup.gse.gimbal.device

    gimbal.deactivate_control_loop()

@building_block
def inta_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at INTA such that the illuminated position is at the given angular distance from the
    optical axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - wait: Whether or not to wait for the stages to reach the commanded positions.
    """
    """  
    Old conversions 
    grx    = theta * np.cos(np.deg2rad(phi+90))
    gry    = theta * np.sin(np.deg2rad(phi+90))    
    """
    
    grx = np.rad2deg(-np.arcsin(np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))))
    gry = np.rad2deg(np.arctan2(np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)), np.cos(np.deg2rad(theta))))



    ret, _ = gimbal_check_absolute_movement(grx=grx, gry=gry)
    if ret != 0:
        logging.error(
            f"Error: Out of bounds! The position with theta = {theta} and phi = {phi} (GRx = {grx} and GRy = {gry})"
            f" is outside the user limits. Aborting...")
        raise Abort(
            f"Error: Out of bounds! The position with theta = {theta} and phi = {phi} (GRx = {grx} and GRy = {gry})"
            f" is outside the user limits. Aborting...")

    gimbal_move_absolute(grx=grx, gry=gry, wait=wait)
    pos = gimbal_request_user_positions()

    logging.info(f"Gimbal reached requested position ({pos[0]}, {pos[1]})")



@building_block
def inta_point_source_to_fov_translation(theta=None, phi=None, translation_z=None, wait=True):
    inta_point_source_to_fov(theta=theta, phi=phi, wait=wait)

@building_block
def inta_point_source_to_fp(x=None, y=None, wait=None):
    """ Position source on (x,y).

    Position the EGSE mechanisms at INTA such that the illuminated position is at the given focal-plane coordinates.

    Args:
        - x: Focal-plane x-coordinate to move to [mm].
        - y: Focal-plane y-coordinate to move to [mm].
        - wait: Whether or not to wait for the mechanisms to reach the commanded positions.
    """

    theta, phi = coordinates.focal_plane_coordinates_to_angles(x, y)

    inta_point_source_to_fov(theta, phi, wait)

def inta_enable():
    """ Enable control of the camera rotation mechanism for pointing, for INTA.
    This function initializes the Gimbal:
    1) clear errors
    2) activate Control On
    3) configure coordinates system
    4) go to zero position.

    This function should never be called from a test script.  Instead, call the generic function enable().
    """

    # 1)
    gimbal_clear_error()

    # 2)
    gimbal_activate_control_loop()

    # 3)
    gimbal_configure_offsets()

    # 4)
    gimbal_goto_zero_position(wait=True)


def inta_disable():
    """ Move the camera rotation mechanism to the equilibrium position and release the controller, for INTA.

    When pointing is not needed (e.g during warm up phases), the camera rotation mechanisms is moved to the
    equilibrium position and the controller is released.

    This function should never be called from a test script.  Instead, call the generic function disable().
    """

    # Clear any previous errors
    gimbal_clear_error()

    # Make sure the offsets are zero
    gimbal_reset_offsets()

    # In our case, we identify the equilibrium position with the user zero.
    gimbal_goto_zero_position(wait=True)

    # Position reached. Ready to disable the control loop
    gimbal_deactivate_control_loop()
