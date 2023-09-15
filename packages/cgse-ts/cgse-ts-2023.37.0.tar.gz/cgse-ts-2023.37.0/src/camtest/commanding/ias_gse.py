"""
IAS-specific GSE:  Commanding the mechanisms at IAS
08/09/21 Modifications by Claudia:
* is_in_position() calls have been replaced by is_hexapod_ready() as it is a more robust BB that looks if both
the hexapod momevent is stopped and if the position has been reached.
* Add of the
"""
import logging
import time
from math import radians, sin, cos
import numpy as np

from camtest.core.exec import building_block
from egse import coordinates
from egse.settings import Settings
from egse.state import GlobalState
from egse.exceptions import Abort

FOV_SETTINGS = Settings.load("Field-Of-View")


################################################################################
### COMMANDING THE ZONDA HEXAPOD
################################################################################

#### BB TO MOVE THE HEXAPOD

@building_block
def hexapod_zonda_move_relative_user(
    translation=None,
    rotation=None,
    wait=None,
):

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.move_relative_user(*translation, *rotation)

    if wait:

        while not is_hexapod_ready():

            time.sleep(granularity)

@building_block
def hexapod_zonda_move_relative_object(
    translation=None,
    rotation=None,
    wait=None
):
    """ Move the hexapod in HEX_OBJ, relative to the current situation.

    Move the hexapod relative to its current position and orientation. The
    relative movement is expressed in the (invariant) user coordinate system.

    Args:
        - translation: 3x1 vector = requested tranlation along the x,y,z-axes of HEX_OBJ [mm].
        - rotation   : 3x1 vector = requested rotation angles over the x,y,z-axes of HEX_OBJ [degrees].
        - wait: Whether or not to wait for the hexapod to reach its commanded positions.
    """

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.move_relative_object(*translation, *rotation)

    if wait:

        while not is_hexapod_ready():

            time.sleep(granularity)

@building_block
def hexapod_zonda_move_absolute(
    translation=None,
    rotation=None,
    wait=None,
):

    """ Move the hexapod in HEX_USR, in an absolute sense.

    Move the hexapod to the given position and orientation. The
    absolute movement is expressed in the object coordinate system.

    Args:
        - translation: 3x1 vector = requested final x,y,z position of the origin of HEX_OBJ in HEX_USR [mm].
        - rotation   : 3x1 vector = requested final x,y,z orientation of the HEX_OBJ axes wrt HEX_USR [degrees].
        - wait: Whether or not to wait for the hexapod to reach its commanded positions.

    """

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.move_absolute(*translation, *rotation)

    if wait:

        while not is_hexapod_ready():

            time.sleep(granularity)

@building_block
def hexapod_zonda_goto_retracted_position(wait=None):
    """ Move the hexapod to the retracted position.

    Args:
        - wait: boolean - Whether or not to wait for the hexapod to reach its retracted
                position.
    """

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.goto_retracted_position()

    # Wait for the Zonda hexapod to reach the retracted position

    if wait:

        while not is_hexapod_ready():

            time.sleep(granularity)

@building_block
def hexapod_zonda_goto_zero_position(wait=None):
    """ Move the hexapod to the zero position.

    Args:
        - wait: boolean - Whether or not to wait for the hexapod to reach its retracted
                position.
    """

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.goto_zero_position()

    # Wait for the Zonda hexapod to reach the zero position

    if wait:

        while not is_hexapod_ready():
            time.sleep(granularity)


#### BB TO CHECK THE HEXAPOD STATUS

@building_block
def hexapod_zonda_request_user_positions():
    """Returns the user positions of the Hexapod as an array of floats.

    Returns: [Tx, Ty, Tz, Rx, Ry, Rz].
        Tx, Ty, Tz: Translation in X, Y, and Z
        Rx, Ry, Rz: Rotation in X, Y, and Z
    """
    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_user_positions()

@building_block
def hexapod_zonda_request_machine_positions():
    """Returns the machine positions of the Hexapod as an array of floats.

    Returns: [Tx, Ty, Tz, Rx, Ry, Rz].
        Tx, Ty, Tz: Translation in X, Y, and Z
        Rx, Ry, Rz: Rotation in X, Y, and Z
    """
    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_machine_positions()

@building_block
def hexapod_check_absolute_movement(
    translation=None,
    rotation=None,
):

    """ Checks the hexapod in HEX_USR, in an absolute sense.

    Checks the hexapod to the given position and orientation. The
    absolute movement is expressed in the object coordinate system.

    Args:
        - translation: 3x1 vector = requested final x,y,z position of the origin of HEX_OBJ in HEX_USR [mm].
        - rotation   : 3x1 vector = requested final x,y,z orientation of the HEX_OBJ axes wrt HEX_USR [degrees].

    """

    hexapod = GlobalState.setup.gse.hexapod.device
    return hexapod.check_absolute_movement(*translation, *rotation)

@building_block
def hexapod_check_relative_object_movement(
    translation=None,
    rotation=None,
):

    """ Checks the hexapod in HEX_USR, in an absolute sense.

    Checks the hexapod to the given position and orientation.

    Args:
        - translation: 3x1 vector = requested final x,y,z position of the origin of HEX_OBJ in HEX_USR [mm].
        - rotation   : 3x1 vector = requested final x,y,z orientation of the HEX_OBJ axes wrt HEX_USR [degrees].

    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.check_relative_object_movement(*translation, *rotation)


@building_block
def hexapod_get_limits_state():
    """ Return workspace limits enable state
    return a dictionnary: Limit states of the different work spaces (factory, machine and user)
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_limits_state()


@building_block
def hexapod_user_limit_enable(state: int):
    """ Enables (1) or disables (0) the user workspace limits of the hexapod.
    Args:
        - 1 to enable
        - 0 to disable
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.user_limit_enable(state)


@building_block
def hexapod_get_cordinates_systems():

    """ Retrieve the definition of the User Coordinate System and the Object Coordinate System.
    Returns tx_u, ty_u, tz_u, rx_u, ry_u, rz_u, tx_o, ty_o, tz_o, rx_o, ry_o, rz_o where the translation parameters are
    in [mm] and the rotation parameters are in [deg].
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_coordinates_systems()

@building_block
def hexapod_configure_coordinates_systems():

    """ Configure the User Coordinate System and the Object Coordinate System taken from the setup file.
    """

    coord_sys = GlobalState.setup.camera.fov.pupil_coordinates
    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.configure_coordinates_systems(*coord_sys)


@building_block
def hexapod_get_speed():

    """ Retrieve the configuration of the movement speed.

                        vt is the translation speed of the hexapod in mm per second [mm/s]
                        vr is the angular speed of the hexapod in deg per second [deg/s]
                        vt_min, vt_max are the limits for the translation speed [mm/s]
                        vr_min, vr_max are the limits for the angular speed [mm/s]
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_speed()

@building_block
def is_hexapod_in_position():
    """ Checks whether the hexapod is in position and not moving.

    Returns:
        - True if the hexapod is in position and not moving; False otherwise.
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.is_in_position()

@building_block
def hexapod_general_state():
    """ Checks whether the hexapod is in position and not moving.

    Returns:
        - True if the hexapod is in position and not moving; False otherwise.
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    return hexapod.get_general_state()

@building_block
def is_hexapod_ready():
    """ Checks whether the hexapod is in position and not moving.

    Returns:
        - True if the hexapod is in position and not moving; False otherwise.
    """
    state = hexapod_general_state()

    # Checks both if the hexapod reached a position and there is no error
    if state[1][3] and not state[1][0]:
        return True
    else:
        return False

@building_block
def hexapod_clear_error():
    """
    Clear all errors in the controller software.
    """
    hexapod = GlobalState.setup.gse.hexapod.device

    hexapod.clear_error()

@building_block
def hexapod_activate_control_loop():
    """
    Clear all errors in the controller software.
    """
    hexapod = GlobalState.setup.gse.hexapod.device

    hexapod.activate_control_loop()


#####################################
#### BB TO CONFIGURE THE HEXAPOD
##################################

@building_block
def hexapod_set_speed(
    vt=None,
    vr=None,

):

    """ Set the speed of the hexapod movements according to vt and vr arguments.

                        vt is the translation speed of the hexapod in mm per second [mm/s]
                        vr is the angular speed of the hexapod in deg per second [deg/s]

                        The parameters vt and vr are automatically limited by the controller between the factory
                        configured minimum and maximum speed
    """

    hexapod = GlobalState.setup.gse.hexapod.device

    hexapod.set_speed(vt, vr)

    logging.info(f"The hexapod speed has been set to: {hexapod_get_speed}")



################################################################################
### GLOBAL GSE POSITIONNING
################################################################################


@building_block
def ias_point_source_to_fov_translation(theta=None, phi=None, translation_z=None,  wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at IAS such that the illuminated position is at the given angular distance from the
    optical axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - translation_z: translation in mm along the vertical axis (positive goes up, negative goes down)
        - wait: Whether or not to wait for the stages to reach the commanded positions.

    2021/09/08 Please note that this BB does not include any coordinate change or reference frame correction as
    discussed and agreed during the alignment meeting held the 31/08/21. This BB only performs a "pure" (theta,phi)
    transformation into rotY and rotZ angles expressed in the Hexapod User reference frame.
    Coordinate changes will be directly introduced in the zonda controller software by a 3rd party user after the
    correct alignment and reference system have been found. The configuration control of these values will be managed
    by TBD.
    """

    # No bias assumed we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FP
    if translation_z is None:
        translation = [0, 0, 0]
    else:
        translation=[0, 0, translation_z] # translation_z in mm

    # No bias assumed we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FP

    rotX = 0

    # No correction, we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FPA reference frames are collinear now

    rotZ = -np.arcsin(np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi)))
    rotZ = np.rad2deg(rotZ)

    rotY = np.arctan(np.tan(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)))
    rotY = np.rad2deg(rotY)

    # Check if the desired position is reachable (under the user limits)
    state = hexapod_check_absolute_movement(translation=translation, rotation=[rotX, rotY, rotZ])
    if state[0] != 0:
        logging.error(
            f"Error: Out of bounds! The position with theta = {theta} and phi = {phi} (rotY = {rotY} and rotZ = {rotZ})"
            f" is outside the user limits. Aborting...")
        raise Abort(
            f"Error: Out of bounds! The position with theta = {theta} and phi = {phi} (rotY = {rotY} and rotZ = {rotZ})"
            f" is outside the user limits. Aborting...")

    hexapod_zonda_move_absolute(translation=translation, rotation=[rotX, rotY, rotZ], wait=wait)

    position = hexapod_zonda_request_user_positions()

    logging.info(f"The hexapod reached the requested position: {position}")


@building_block
def ias_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at IAS such that the illuminated position is at the given angular distance from the
    optical axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - wait: Whether or not to wait for the stages to reach the commanded positions.

    2021/09/08 Please note that this BB does not include any coordinate change or reference frame correction as
    discussed and agreed during the alignment meeting held the 31/08/21. This BB only performs a "pure" (theta,phi)
    transformation into rotY and rotZ angles expressed in the Hexapod User reference frame.
    Coordinate changes will be directly introduced in the zonda controller software by a 3rd party user after the
    correct alignment and reference system have been found. The configuration control of these values will be managed
    by TBD.
    """

    # No bias assumed we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FP

    translation = [0, 0, 0]

    # No bias assumed we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FP

    rotX = 0

    # No correction, we assume we are rotating around the pupil (user ref.frame) and that the pupil ref frame, the
    # collimator and the FPA reference frames are collinear now

    rotZ = -np.arcsin(np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi)))
    rotZ = np.rad2deg(rotZ)

    rotY = np.arctan(np.tan(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)))
    rotY = np.rad2deg(rotY)

    hexapod_zonda_move_absolute(translation=translation, rotation=[rotX, rotY, rotZ], wait=wait)

    position = hexapod_zonda_request_user_positions()

    logging.info(f"The hexapod reached the requested position.\n"
                 f"The position measured by hexapod sensors is (Tx, Ty, Tz, Rx, Ry, Rz): {position}.\n"
                 f"Input angles were theta={theta} and phi={phi}")


@building_block
def ias_point_source_to_fp(x=None, y=None, wait=None):
    """ Position source on (x,y).

    Position the EGSE mechanisms at IAS such that the illuminated position is at the given focal-plane coordinates.

    Args:
        - x: Focal-plane x-coordinate to move to [mm].
        - y: Focal-plane y-coordinate to move to [mm].
        - wait: Whether or not to wait for the mechanisms to reach the commanded positions.
    """

    x_undistorted, y_undistorted = coordinates.undistorted_to_distorted_focal_plane_coordinates(
        x, y, FOV_SETTINGS.DISTORTION_COEFFICIENTS, focal_length=FOV_SETTINGS.FOCAL_LENGTH
    )

    theta, phi = coordinates.focal_plane_coordinates_to_angles(x_undistorted, y_undistorted)
    ias_point_source_to_fov(theta=theta, phi=phi, wait=wait)

    return theta, phi


def ias_enable():
    """ Enable control of the camera rotation mechanism for pointing, for IAS.
    This function initializes the zonda:
    1) clear errors
    2) activate Control On
    3) configure coordinates system
    4) enable limits if they are disable
    5) go to zero position.

    This function should never be called from a test script.  Instead, call the generic function enable().
    """

    # 1)
    hexapod_clear_error()

    # 2)
    hexapod_activate_control_loop()

    # 3)
    hexapod_configure_coordinates_systems()

    # 4)
    user_limits_state = hexapod_get_limits_state()["User workspace limits"]
    if user_limits_state == 0:
        hexapod_user_limit_enable(state=1)

    # 5)
    hexapod_zonda_goto_zero_position(wait=True)


def ias_disable():
    """ Move the camera rotation mechanism to the equilibrium position and release the controller, for IAS.

    When pointing is not needed (e.g during warm up phases), the camera rotation mechanisms is moved to the
    equilibrium position and the controller is released.

    This function should never be called from a test script.  Instead, call the generic function disable().
    """

    raise NotImplementedError