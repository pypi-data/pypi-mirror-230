"""
CSL-specific GSE:  Commanding the mechanisms at CSL (hexpod + stages)
"""
import logging

import time
from math import radians
from math import tan

import numpy as np
from scipy.interpolate import interp1d

from camtest.core.exec import building_block
from egse import coordinates
from egse.coordinates.avoidance import is_avoidance_ok
from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Interface, HuberSMC9300Proxy
from egse.state import GlobalState
# FIXME: visit_field_angles seems not to exist anymore in visitedpositions
from egse.system import wait_until

# TODO How to select the settings from the appropriate project?
# from egse.visitedpositions import FIELD_ANGLES_SIGNAL, FOCAL_PLANE_SIGNAL

LOGGER = logging.getLogger(__name__)

STAGES_SETTINGS = Settings.load("Huber Controller")
FOV_SETTINGS = Settings.load("Field-Of-View")
# VISITED_POSITIONS_UI_SETTINGS = Settings.load("Visited Positions UI")

####################################################
### STATUS QUERIES
####################################################

def is_all_in_position():
    """ Checks whether mechanisms are in position and not moving.

    Returns:
        True if all mechanisms are in position and not moving; False otherwise.
    """

    if is_rotation_stage_connected() and not is_rotation_stage_in_position():
            return False

    if is_sma_rotation_connected() and not is_sma_rotation_in_position():
        return False

    if is_sma_translation_connected() and not is_sma_translation_in_position():
        return False

    return is_hexapod_in_position()


def is_rotation_stage_connected():

    # TODO

    return True

def is_sma_rotation_connected():

    # TODO

    return False

def is_sma_translation_connected():

    # TODO

    return False

def wait_all_in_position():
    """ Wait until all mechanisms are in position.
    """

    granularity = GlobalState.setup.gse.hexapod.time_request_granularity    # TODO

    while not is_all_in_position:

        time.sleep(granularity)


def get_rotation_stage_position():
    """ Returns the position of the big rotation stage.

    Return: Position of the big rotation stage [degrees].
    """
    stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device

    return stages.get_current_position(axis=STAGES_SETTINGS.BIG_ROTATION_STAGE)


def get_sma_rotation_position():
    """ Returns the position of the small rotation stage.

    Return: Position of the small rotation stage [degrees].
    """
    stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device

    return stages.get_current_position(axis=STAGES_SETTINGS.SMALL_ROTATION_STAGE)


def get_sma_translation_position():
    """ Returns the position of the translation stage.

    Returns: Position of the translation stage [mm].
    """
    stages: HuberSMC9300Interface = GlobalState.setup.gse.stages.device

    return stages.get_current_position(axis=STAGES_SETTINGS.TRANSLATION_STAGE)




################################################################################
### COMMANDING THE STAGES
################################################################################


@building_block
def rotation_stage_move(angle=None):
    """ Move the big rotation stage to the given angle.

    Args:
        angle (float): A positive angle corresponds to a counter-clockwise rotation.
            [degrees]
    """

    stages = GlobalState.setup.gse.stages.device

    # Do NOT use a wait=True here, because that will cause the communication between the
    # control server and the proxy to be ended by a timeout and a message that the control
    # server seems to be off-line.

    stages.goto(STAGES_SETTINGS.BIG_ROTATION_STAGE, angle, False)


def is_rotation_stage_in_position():
    """ Checks whether the big rotation stage is in position and not moving.

    Returns:
        - True if the big rotation stage is in position and not moving; False otherwise.
    """

    stages = GlobalState.setup.gse.stages.device

    return stages.is_in_position(STAGES_SETTINGS.BIG_ROTATION_STAGE)


@building_block
def sma_rotation_move(angle=None):
    """ Move the small rotation stage to the given angle.

    Args:
        - angle: Rotation angle [degrees]. A rotation angle of zero degrees corresponds to a
            vertical position
    """

    stages = GlobalState.setup.gse.stages.device

    # Do NOT use a wait=True here, because that will cause the communication between the
    # control server and the proxy to be ended by a timeout and a message that the control
    # server seems to be off-line.

    stages.goto(STAGES_SETTINGS.SMALL_ROTATION_STAGE, angle, False)


def is_sma_rotation_in_position():
    """ Checks whether the small rotation stage is in position and not moving.

    Returns:
        - True if the small rotation stage is in position and not moving; False otherwise.
    """

    stages = GlobalState.setup.gse.stages.device

    return stages.is_in_position(STAGES_SETTINGS.SMALL_ROTATION_STAGE)


@building_block
def sma_translation_move(distance=None):
    """ Move the translation stage to the given angle.

    Args:
        distance (float): Position along the translation stage to move to [mm].
    """

    stages = GlobalState.setup.gse.stages.device

    # Do NOT use a wait=True here, because that will cause the communication between the
    # control server and the proxy to be ended by a timeout and a message that the control
    # server seems to be off-line.

    stages.goto(STAGES_SETTINGS.TRANSLATION_STAGE, distance, False)


def is_sma_translation_in_position():
    """ Checks whether the translation stage is in position and not moving.

    Returns:
        True if the translation stage is in position and not moving; False otherwise.
    """

    stages = GlobalState.setup.gse.stages.device

    return stages.is_in_position(STAGES_SETTINGS.TRANSLATION_STAGE)








################################################################################
### COMMANDING THE HEXAPOD
################################################################################



@building_block
def hexapod_puna_move_relative_user(
    translation=None,
    rotation=None,
    wait=None
):
    """ Move the hexapod in HEX_USR, relative to the current situation.

    Move the hexapod relative to its current position and orientation. The
    relative movement is expressed in the (invariant) user coordinate system.

    Args:
        - translation: 3x1 vector = requested tranlation along the x,y,z-axes of HEX_USR [mm].
        - rotation   : 3x1 vector = requested rotation angles over the x,y,z-axes of HEX_USR [degrees].
        - wait: Whether or not to wait for the hexapod to reach its commanded positions.
    """

    setup = GlobalState.setup

    hexapod = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod.move_relative_user(*translation, *rotation)

    if wait:

        while not hexapod.is_in_position():

            time.sleep(granularity)


@building_block
def hexapod_puna_move_relative_object(
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

        while not hexapod.is_in_position():

            time.sleep(granularity)


@building_block
def hexapod_puna_move_absolute(
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

        while not hexapod.is_in_position():

            time.sleep(granularity)


@building_block
def hexapod_puna_move_relative_user_z(delta_z=None, wait=None):
    """ Move the hexapod along the z-axis of HEX_USR.

    Move the hexapod over the given distance along the z-axis of HEX_USR.

    Args:
        - delta_z: Distance along the z-axis of HEX_USR to move the
                   hexapod over [mm].
        - wait: Whether or not to wait for the hexapod to reach its
                commanded positions.
    """

    hexapod_puna_move_relative_user(
        translation=[0,0,delta_z],
        rotation=[0,0,0],
        wait=wait,
    )


@building_block
def hexapod_puna_move_relative_object_z(delta_z=None, wait=None):
    """ Move the hexapod along the z-axis of HEX_OBJ.

    Move the hexapod over the given distance along the z-axis of HEX_OBJ.

    Args:
        - delta_z: Distance along the z-axis of HEX_OBJ to move the
                   hexapod over [mm].
        - wait: Whether or not to wait for the hexapod to reach its
                commanded positions.
    """

    hexapod_puna_move_relative_object(
        translation=[0,0,delta_z],
        rotation=[0,0,0],
        wait=wait,
    )


@building_block
def hexapod_puna_move_absolute_z(z=None, wait=None):
    """ Move the hexapod along the z-axis of HEX_USR.

    Move the hexapod to the given position on the z-axis of HEX_USR.

    Args:
        - z: Postion on the z-axis of HEX_USR to move the hexapod to [mm].
        - wait: Whether or not to wait for the hexapod to reach its
                commanded positions.
    """

    hexapod_puna_move_absolute(
        translation=[0,0,z],
        rotation=[0,0,0],
        wait=wait,
    )


@building_block
def hexapod_puna_request_user_positions():
    """Returns the user positions of the Hexapod as an array of floats.

    Returns: [Tx, Ty, Tz, Rx, Ry, Rz].
        Tx, Ty, Tz: Translation in X, Y, and Z
        Rx, Ry, Rz: Rotation in X, Y, and Z
    """
    hexapod_puna = GlobalState.setup.gse.hexapod.device

    return hexapod_puna.get_user_positions()


@building_block
def hexapod_puna_goto_retracted_position(wait=None):
    """ Move the hexapod to the retracted position.

    Args:
        - wait: boolean - Whether or not to wait for the hexapod to reach its retracted
                position.
    """

    setup = GlobalState.setup

    hexapod_puna = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod_puna.goto_retracted_position()

    # Wait for the Puna hexapod to reach the retracted position

    if wait:

        while not hexapod_puna.is_in_position():

            time.sleep(granularity)

@building_block
def hexapod_puna_goto_zero_position(wait=None):
    """ Move the hexapod to the zero position.

    Args:
        - wait: boolean - Whether or not to wait for the hexapod to reach its retracted
                position.
    """

    setup = GlobalState.setup

    hexapod_puna = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod_puna.goto_zero_position()

    # Wait for the Puna hexapod to reach the zero position

    if wait:

        while not hexapod_puna.is_in_position():

            time.sleep(granularity)


@building_block
def hexapod_puna_homing(wait=None):
    """ Move the hexapod to the retracted position.

    Args:
        - wait: boolean - Whether or not to wait for the hexapod to end the homing
    """

    setup = GlobalState.setup

    hexapod_puna = setup.gse.hexapod.device
    granularity = setup.gse.hexapod.time_request_granularity

    hexapod_puna.homing()

    # Wait for the Puna hexapod to finish the homing procedure and reach the 0 position

    if wait:

        while (not hexapod_puna.is_homing_done()) or (not hexapod_puna.is_in_position()):

            time.sleep(granularity)

def is_hexapod_in_position():
    """ Checks whether the hexapod is in position and not moving.

    Returns:
        - True if the hexapod is in position and not moving; False otherwise.
    """

    hexapod_puna = GlobalState.setup.gse.hexapod.device

    return hexapod_puna.is_in_position()








################################################################################
### CHECK AVOIDANCE VOLUME, AND MOVE THE HEXAPOD
################################################################################

@building_block
def check_and_move_absolute(cslmodel=None, translation=None, rotation=None, setup=None, verbose=True):
    from camtest.commanding.csl_gse import hexapod_puna_move_absolute

    cslmodel.hexapod_move_absolute(translation,rotation)

    avoidance_respected = is_avoidance_ok(cslmodel.get_frame("hexusr"), cslmodel.get_frame("hexobj"), setup=setup, verbose=True)

    accepted = True

    if avoidance_respected:

        if verbose:
            print(f"Movement accepted:")

        hexapod_puna_move_absolute(translation=translation,rotation=rotation,wait=True)

    else:

        accepted = False
        print("Movement refused:")

    if verbose or not accepted:
        print(f"                {np.round(translation,6)}")
        print(f"                {np.round(rotation,6)}")

    return accepted

@building_block
def check_and_move_relative_user(cslmodel=None, translation=None, rotation=None, setup=None, verbose=True):
    from camtest.commanding.csl_gse import hexapod_puna_move_relative_user

    cslmodel.hexapod_move_relative_user(translation,rotation)

    avoidance_respected = is_avoidance_ok(cslmodel.get_frame("hexusr"), cslmodel.get_frame("hexobj"), setup=setup, verbose=True)

    accepted = True

    if avoidance_respected:

        if verbose:
            print(f"Movement accepted:")

        hexapod_puna_move_relative_user(translation=translation,rotation=rotation,wait=True)

    else:

        accepted = False
        print("Movement refused:")

    if verbose or not accepted:
        print(f"                {np.round(translation,6)}")
        print(f"                {np.round(rotation,6)}")

    return accepted

@building_block
def check_and_move_relative_object(cslmodel=None, translation=None, rotation=None, setup=None, verbose=True):
    from camtest.commanding.csl_gse import hexapod_puna_move_relative_object

    cslmodel.hexapod_move_relative_object(translation,rotation)

    avoidance_respected = is_avoidance_ok(cslmodel.get_frame("hexusr"), cslmodel.get_frame("hexobj"), setup=setup, verbose=True)

    accepted = True

    if avoidance_respected:

        if verbose:
            print(f"Movement accepted:")

        hexapod_puna_move_relative_object(translation=translation,rotation=rotation,wait=True)

    else:

        accepted = False
        print("Movement refused:")

    if verbose or not accepted:
        print(f"                {np.round(translation,6)}")
        print(f"                {np.round(rotation,6)}")

    return accepted


def positions_match(hexapod, hexsim, atol=0.0001, rtol=0.0001):
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)


def is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    if verbose is None: verbose = ""

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(model.get_frame('hexobj'))
    coomod = np.concatenate([coomodtr, coomodrot])

    print(f"{verbose}Hexapod   : {np.round(coohex, rounding)}")
    print(f"{verbose}Model     : {np.round(coomod, rounding)}")
    print(f"{verbose}Diff      : {np.round(coohex - coomod, rounding)}")

    is_sync = np.allclose(coohex, coomod, atol=atol, rtol=rtol)

    print(f"{verbose}In synch  : {is_sync}")

    return is_sync


def hex_positions(hexapod, rounding=3):
    """
    Print User and machine coordinates of the input Hexapod

    Parameters
    ----------
    hexapod : Hexapod

    Returns
    -------
    None

    """
    print(f"OBJ vs USR: {np.round(hexapod.get_user_positions(), rounding)}")
    print(f"PLT vs MEC: {np.round(hexapod.get_machine_positions(), rounding)}")
    return


################################################################################
### GLOBAL GSE POSITIONNING
################################################################################

@building_block
def csl_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at CSL (i.c. Huber stages) such that the
    illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane
    (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle)
               [degrees].
        - wait: Whether or not to wait for the stages to reach the
                commanded positions.
    """

    LOGGER.info(f"Position source on (theta, phi) = ({theta}, {phi})")

    setup = GlobalState.setup

    theta_correction = False
    sma_correction = False

    stages: HuberSMC9300Interface = setup.gse.stages.device

    offset_phi = setup.gse.stages.calibration.offset_phi
    offset_alpha = setup.gse.stages.calibration.offset_alpha
    offset_delta_x = setup.gse.stages.calibration.offset_delta_x

    if theta_correction:
        frequency = setup.gse.stages.theta_correction_coefficients.frequency
        amplitude = setup.gse.stages.theta_correction_coefficients.amplitude
        phase     = setup.gse.stages.theta_correction_coefficients.phase
        offset    = setup.gse.stages.theta_correction_coefficients.offset

        correction = -1. * (np.sin(phi * frequency + phase) * amplitude + offset)

        theta = theta + correction

    # Azimuth correction wrt the misalignment of the SMA mirror
    # SMA misalignment sends the source to too high phi (SMA misalignment = +10 arcmin rotation around z)
    # phi_correction is negative & must be added to phi
    if sma_correction:
        calib_theta = setup.gse.stages.calibration.big_rotation_azimuth_correction[0]
        calib_phi   = setup.gse.stages.calibration.big_rotation_azimuth_correction[1]
        interpolator = interp1d(calib_theta, calib_phi, kind='linear')

        phi_correction = interpolator(theta)

    else:
        phi_correction = 0.

    # In-field angle (phi) [degrees]
    #   -> big rotation stage

    rotation_stage_move(angle=-(phi - offset_phi + phi_correction))

    # Angular distance from the optical axis [degrees]
    #   -> scan mirror assembly (small rotation stage)

    k1, k2 = setup.gse.stages.calibration.sma_rotation_correction

    alpha = theta / 2.0 + k1 * theta + k2 * pow(theta, 2)
    sma_rotation_move(angle=alpha - offset_alpha)

    # Translation of the SMA [mm]
    #   -> scan mirror assembly (translation stage)

    height_collimated_beam = setup.gse.stages.calibration.height_collimated_beam

    delta_x = height_collimated_beam * tan(radians(theta))
    sma_translation_move(distance=-(delta_x - offset_delta_x))

    # Wait until the stages have stopped moving before exiting
    # Limiting factor: big rotation stage:
    #   - angular speed: 1 degree for 10000 units of speed
    #   - maximum amplitude of movement: 360 degree

    try:

        with HuberSMC9300Proxy() as proxy:

            speed_big_rotation_stage = float(proxy.get_slew_speed(STAGES_SETTINGS.BIG_ROTATION_STAGE))

    except:

        speed_big_rotation_stage = setup.gse.stages.big_rotation_stage.default_speed

    timeout = 360 / speed_big_rotation_stage * 10000

    if wait:
        wait_until(lambda:
                   stages.is_in_position(STAGES_SETTINGS.BIG_ROTATION_STAGE) and stages.is_in_position(
                       STAGES_SETTINGS.SMALL_ROTATION_STAGE) and stages.is_in_position(
                       STAGES_SETTINGS.TRANSLATION_STAGE), timeout=timeout, interval=0.5)

    # show_visited_position_angles(theta, phi)
    # visit_field_angles(theta, phi)


@building_block
def csl1_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at CSL (i.c. Huber stages) such that the
    illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane
    (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle)
               [degrees].
        - wait: Whether or not to wait for the stages to reach the
                commanded positions.

    REF : PLATO-CSL-PL-RP-0031 v1.0 Calibration Report R1_0 / R1_M (22-11-2022)
    """

    LOGGER.info(f"Position source on (theta, phi) = ({theta}, {phi})")

    setup = GlobalState.setup

    stages: HuberSMC9300Interface = setup.gse.stages.device

    offset_phi = setup.gse.stages.calibration.offset_phi
    offset_alpha = setup.gse.stages.calibration.offset_alpha
    offset_delta_x = setup.gse.stages.calibration.offset_delta_x

    # BIG ROTATION STAGE
    # In-field angle (phi) [degrees]
    #   -> big rotation stage

    phi_coeffs = setup.gse.stages.calibration.phi_correction_coefficients

    phi_correction = phi_coeffs[1] * theta + phi_coeffs[0]

    phi_comm = -(phi + phi_correction) - offset_phi

    rotation_stage_move(angle=phi_comm)


    # SMA ROTATION
    # Angular distance from the optical axis [degrees]
    #   -> scan mirror assembly (small rotation stage)

    alpha_coeffs = setup.gse.stages.calibration.alpha_correction_coefficients

    alpha = alpha_coeffs[1] * theta + alpha_coeffs[0] - offset_alpha

    sma_rotation_move(angle=alpha)


    # SMA TRANSLATION
    #   -> scan mirror assembly (translation stage)

    delta_x_coeffs = setup.gse.stages.calibration.delta_x_correction_coefficients
    height_collimated_beam = setup.gse.stages.calibration.height_collimated_beam

    delta_x_correction = delta_x_coeffs[2] * theta * theta + delta_x_coeffs[1] * theta + delta_x_coeffs[0]

    delta_x = -1 * (height_collimated_beam * tan(radians(theta)) + delta_x_correction - offset_delta_x)

    sma_translation_move(distance=delta_x)

    # FINAL WAIT
    # Wait until the stages have stopped moving before exiting
    # Limiting factor: big rotation stage:
    #   - angular speed: 1 degree for 10000 units of speed
    #   - maximum amplitude of movement: 360 degree

    try:

        with HuberSMC9300Proxy() as proxy:

            speed_big_rotation_stage = float(proxy.get_slew_speed(STAGES_SETTINGS.BIG_ROTATION_STAGE))

    except:

        speed_big_rotation_stage = setup.gse.stages.big_rotation_stage.default_speed

    timeout = 360 / speed_big_rotation_stage * 10000

    if wait:
        wait_until(lambda:
                   stages.is_in_position(STAGES_SETTINGS.BIG_ROTATION_STAGE) and stages.is_in_position(
                       STAGES_SETTINGS.SMALL_ROTATION_STAGE) and stages.is_in_position(
                       STAGES_SETTINGS.TRANSLATION_STAGE), timeout=timeout, interval=0.5)


@building_block
def csl2_point_source_to_fov(theta=None, phi=None, wait=None):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms at CSL Room 2 (i.c. Huber stages) such that the
    illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane
    (phi).

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle)
               [degrees].
        - wait: Whether or not to wait for the stages to reach the
                commanded positions.

    REF :
    """
    # At this point, the relation between the configuration of the Huber Stages and the source position is considered
    # the same for CSL2 as for CSL1 (only the calibration of the Huber Stages is potentially different in the setup)
    
    csl1_point_source_to_fov(theta=theta, phi=phi, wait=wait)

@building_block
def csl_point_source_to_fov_translation(theta=None, phi=None, translation_z=None, wait=True):

    raise NotImplementedError

# def show_visited_position_angles(theta, phi):
#     """ Show the given position in the visited-positions GUI.
#
#     Args:
#         - theta: Angular distance from the optical axis [degrees].
#         - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
#     """
#
#     context = zmq.Context.instance()
#     socket = context.socket(zmq.PUSH)
#
#     protocol = VISITED_POSITIONS_UI_SETTINGS.PROTOCOL
#     hostname = VISITED_POSITIONS_UI_SETTINGS.HOSTNAME
#     port = VISITED_POSITIONS_UI_SETTINGS.PORT
#
#     socket.connect(connect_address(protocol, hostname, port))
#
#     data = {"theta": theta, "phi": phi}
#     pickle_string = pickle.dumps(data)
#
#     socket.send(pickle_string)
#     socket.close()


@building_block
def csl_point_source_to_fp(x=None, y=None, wait=None) -> (float, float):
    """ Position source on (x,y).

    Position the EGSE mechanisms at CSL (i.c. Huber stages) such that the
    illuminated position is at the given focal-plane coordinates.

    Args:
        - x: Focal-plane x-coordinate to move to [mm].
        - y: Focal-plane y-coordinate to move to [mm].
        - wait: Whether or not to wait for the stages to reach the
                commanded positions.
    """

    x_undistorted, y_undistorted = coordinates.undistorted_to_distorted_focal_plane_coordinates(
        x, y, FOV_SETTINGS.DISTORTION_COEFFICIENTS, focal_length=FOV_SETTINGS.FOCAL_LENGTH
    )

    theta, phi = coordinates.focal_plane_coordinates_to_angles(x_undistorted, y_undistorted)
    csl_point_source_to_fov(theta=theta, phi=phi, wait=wait)

    return theta, phi


def csl_enable():
    """ Enable control of the camera rotation mechanism for pointing, for INTA.

    This function should never be called from a test script.  Instead, call the generic function enable().
    """

    pass


def csl_disable():
    """ Move the camera rotation mechanism to the equilibrium position and release the controller, for INTA.

    When pointing is not needed (e.g during warm up phases), the camera rotation mechanisms is moved to the
    equilibrium position and the controller is released.

    This function should never be called from a test script.  Instead, call the generic function disable().
    """

    pass
