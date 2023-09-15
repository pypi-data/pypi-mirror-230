from camtest import building_block
from egse.exceptions import Abort
from egse.state import GlobalState
from egse.tcs.tcs import OperatingMode
from egse.tcs.tcs import TCSInterface


@building_block
def set_operating_mode(mode: OperatingMode):
    """ Set the operating mode of the TCS.

    Args:
        - mode: New operating mode for the TCS.

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if is_task_running():
        raise Abort("Cannot change operating mode, as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    tcs.set_operating_mode(mode)
    tcs.commit()


@building_block
def set_closed_loop_mode(channel: str, mode: int):
    """Sets the closed-loop mode for the given channel.

    The mode can take the following values:

    * 0 = PI, algorithm 1
    * 1 = PI, algorithm 2
    * 2 = Bang-Bang, algorithm 1
    * 3 = Bang-Bang, algorithm 2

    Note that in NORMAL operating mode, the closed-loop mode can only be [0, 1] while in EXTENDED
    operating mode, the closed-loop mode can be [0, 1, 2, 3].

    Args:
        channel (str): one of 'ch1' , 'ch2'
        mode (int): the type of control to use for PWM calculations
    """

    if is_task_running():
        raise Abort("Cannot set closed-loop mode, as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    if channel == "ch1":
        response = tcs.set_parameter("ch1_closedloop_mode", mode)
    elif channel == "ch2":
        response = tcs.set_parameter("ch2_closedloop_mode", mode)
    else:
        raise Abort(f"Incorrect argument: channel shall be 'ch1' or 'ch2', {channel} given.")

    if response != "acknowledge_parameter_change":
        raise Abort(f"Could not set parameters: {response}")




@building_block
def set_pi_parameters(channel: str, ki: float, kp: float, pmax: float):
    """Sets the PI control parameters for the given channel.

    Args:
        channel (str): one of 'ch1' , 'ch2'
        ki (float): integral gain
        kp (float): proportional gain
        pmax (float): maximum power delivered to the heater [mW]
    """
    if is_task_running():
        raise Abort("Cannot set PI control parameters, as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    if channel == "ch1":
        response = tcs.set_parameters(
            ch1_pi_parameters_ki=ki, ch1_pi_parameters_kp=kp, ch1_pmax=pmax)
    elif channel == "ch2":
        response = tcs.set_parameters(
            ch2_pi_parameters_ki=ki, ch2_pi_parameters_kp=kp, ch2_pmax=pmax)
    else:
        raise Abort(f"Incorrect argument: channel shall be 'ch1' or 'ch2', {channel} given.")

    if response != "acknowledge_parameter_change":
        raise Abort(f"Could not set parameters: {response}")

    response = tcs.commit()
    if not response.startswith("acknowledge_commit"):
        raise Abort(f"Couldn't commit configuration settings: {response}")
    else:
        UserWarning(response)


def is_task_running():
    """ Check whether a task is running on the TCS EGSE.

    Returns: True if a task is running on the TCS EGSE; False otherwise.
    """

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    return tcs.is_task_running()


@building_block
def start_task():
    """ Stores previously sent configuration parameters and runs the task."""

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    tcs.run_task()


@building_block
def stop_task():
    """ Stop tasks that are running on the TCS."""

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    tcs.stop_task()


def is_remote_mode_active():
    """ Check whether the Remote Control Mode is active on the TCS EGSE.

    Returns: True of the Remote Control Mode is active on the TCS EGSE; False otherwise.
    """

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device

    return tcs.is_remote_operation_active()


@building_block
def activate_remote_mode():
    """ Activate the Remote Control Mode in the TCS EGSE.

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.request_remote_operation()


@building_block
def deactivate_remote_mode():
    """ End the Remote Control Mode.

    The TCS EGSE will continue with the ongoing task in Local Control Mode.

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.quit_remote_operation()


@building_block
def set_trp1(temperature: float):
    """ Set the temperature setpoint for TRP1.

    Args:
        - temperature: Temperature setpoint for TRP1 [°C].

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if is_task_running():
        raise Abort("Cannot change the TRP1 setpoint, as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.set_parameter(name="ch1_tset", value=temperature)
    tcs.commit()


@building_block
def set_trp1_pmax(pmax: float):
    """ Set the maximum output power for TRP1.

    Defines the maximum power output for the heater output channel. This value
    limits the PWM duty-cycle considering the maximum channel power (20 W for CH1 / TRP1).

    Args:
        - pmax: Maximum output power for TRP1 [mW].

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if is_task_running():
        raise Abort("Cannot change the max output power for TRP1 as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.set_parameter(name="ch1_pmax", value=pmax)
    tcs.commit()


@building_block
def set_trp22(temperature: float):
    """ Set the temperature setpoint for TRP22.

    Args:
        - temperature: Temperature setpoint for TRP22 [°C].

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if is_task_running():
        raise Abort("Cannot change the TRP22 setpoint, as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.set_parameter(name="ch2_tset", value=temperature)
    tcs.commit()


@building_block
def set_trp22_pmax(pmax: float):
    """ Set the maximum output power for TRP22.

    Defines the maximum power output for the heater output channel. This value
    limits the PWM duty-cycle considering the maximum channel power 35 W for CH2 / TRP22).

    Args:
        - pmax: Maximum output power for TRP22 [mW].

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if is_task_running():
        raise Abort("Cannot change the max output power for TRP1 as a task is running on the TCS")

    tcs: TCSInterface = GlobalState.setup.gse.tcs.device
    tcs.set_parameter(name="ch2_pmax", value=pmax)
    tcs.commit()


@building_block
def load_rtd_calibration():
    """Load the calibration for TOU TRP1 and FEE TRP22.

    The calibration information is loaded from the Setup, send to the TCS EGSE and a conversion
    is applied for each RTD that is specified in the Setup. A calibration curve can be either a
    5'th order polynomial for which coefficients (a, b, c, d, e, f) are stored (in that order) in
    the Setup, or it can be the Callendar Van-Dusen equation for which the coefficients (r0, a, b, c)
    are stored in the Setup (also in that order).

    Raises: If a task is already running in the TCS EGSE, an Abort is raised.
    """

    if not is_remote_mode_active():
        raise Abort("Cannot load the RTD calibration, activate remote control mode first.")

    if is_task_running():
        raise Abort("Cannot load the RTD calibration, as a task is running on the TCS")

    setup = GlobalState.setup

    tcs: TCSInterface = setup.gse.tcs.device
    tcs_calibration = setup.gse.tcs.calibration

    for sensor_name, sensor_cal_info in tcs_calibration.sensors.items():

        serial_number = sensor_cal_info.serial_number

        coefficients = tcs_calibration.conversion[sensor_cal_info.conversion]
        if len(coefficients) == 6:
            a, b, c, d, e, f = coefficients
            tcs.upload_polynomial_rtd_parameters(sn=serial_number, a=a, b=b, c=c, d=d, e=e, f=f)
        elif len(coefficients) == 4:
            r0, a, b, c = coefficients
            tcs.upload_callendar_vandusen_rtd_parameters(sn=serial_number, r0=r0, a=a, b=b, c=c)

        tcs.set_rtd_parameters(rtd_id=f"{sensor_name}_cal", sn=serial_number)

    tcs.commit()

# def temp_stabilized() -> bool:
#     """ Check whether the temperatures have stabilised.
#
#     Returns: True if the temperatures have stabilised; False otherwise.
#     """
#
#     return is_trp1_stable() and is_trp10_stable()
#
#
# def wait_camera_stable():
#     """ Wait until the camera temperature is stable.
#
#     The camera temperature is considered stable in case both TRP1 and TRP10 are stable.
#     """
#
#     wait_until(is_trp1_stable() and is_trp10_stable())
#
#
# def is_trp1_stable(tolerance=0.5):
#     """ Check whether the TRP1 temperature is stable.
#
#     TRP1 is considered stable if the actual temperature is within the given tolerance from its setpoint.
#
#     Args:
#         - tolerance: Allowed difference between TRP1 and its setpoint, for TRP1 to be considered stable.
#
#     Returns: True if the TRP1 temperature is stable; False otherwise.
#     """
#
#     return True
#
#     # trp1_now = get_housekeeping("GTCS_T_TRP1_1N")
#     # trp1_setpoint = GlobalState.setup.camera.optimal_focus_temperature
#     #
#     # return abs(trp1_now - trp1_setpoint) < tolerance
#
#
# def is_trp10_stable(tolerance):    # [K/h]?
#     """ Check whether the TRP10 temperature is stable.
#
#     TRP10 is considered stable if its mean rate is within the given tolerance.  The mean rate is calculated over the
#     last 20 minutes.
#
#     Args:
#         - tolerance: Allowed rate for TRP10, for it to be considered stable.
#
#     Returns: True if the TRP10 temperature is stable; False otherwise.
#     """
#
#     return True
#
#     # # Std.dev over last 20min
#     # _, trp10_values = get_housekeeping("GTCS_T_TRP10_1N", time_window=20*60)  # Time window [s]
#     #
#     # np.std(trp10_values)
#     #
#     # # rel_time = finetime[-1] - finetime[0]
#     # return np.mean(np.diff(trp10_values, 1)) / hk_period < tolerance
