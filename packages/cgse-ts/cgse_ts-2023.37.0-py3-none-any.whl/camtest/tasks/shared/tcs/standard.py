import time
from pathlib import Path

from gui_executor.exec import exec_task
from rich import print
from rich.table import Table

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState
from egse.tcs import OperatingMode
from egse.tcs.tcs import TCSInterface
from egse.tcs.tcs import is_tcs_cs_active

UI_MODULE_DISPLAY_NAME = "0 - Standard Procedure Tasks"

ICON_PATH = Path(__file__).parent.resolve() / "icons"


@exec_task(display_name="Set TRP1 setpoint")
def set_trp1(temperature: float):
    """ Sets the TRP1 setpoint.

    This pertains to the Ch1: TOU/TRP1 temperature sensors:
        - TOU_RTD1
        - TOU_RTD2
        - TOU_RTD3

    Args:
        - temperature: Temperature setpoint for TRP1 [°C].
    """

    warning_msg = False  # print a warning message at the end of the task

    if temperature is None or not isinstance(temperature, (float, int)):
        print("[red]You must provide a temperature as a float or int.[/]")
        return

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if not tcs_dev.is_remote_operation_active():
        print("[orange3]WARNING: TCS EGSE not in remote operation mode, activating remote operations..[/]")
        tcs_dev.request_remote_operation()

    obsid = start_observation(f"Set TRP1 temperature to {temperature:.2f}ºC.")
    print(f"Observation started: {obsid}")

    print("Stopping task...")
    response = tcs_dev.stop_task()
    if "remote_mode_not_active" in response:
        print("[red]ERROR: Remote mode still not activated, aborting.[/]")
        end_observation()
        return
    if "no_task_is_running" in response:
        print("[orange3]WARNING: No task was running while attempting to stop the task, continuing...[/]")

    print("waiting 5s ...")
    time.sleep(5.0)  # empirically determined sleep time of 5s

    print("Set extended operating mode...")
    if (response := tcs_dev.set_operating_mode(mode=OperatingMode.EXTENDED)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    print("Set TRP1 setpoint...")
    if (response := tcs_dev.set_parameter(name="ch1_tset", value=temperature)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP1 SETPOINT failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        if "erroneous_configuration" in response:
            print("[orange3]WARNING: The TRP1 temperature values have been corrected by the TCS EGSE.[/]")
            warning_msg = True
        else:
            print(f"[red]ERROR: Setting TRP1 temperature failed: {response}[/]")
            end_observation()
            return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    if (response := tcs_dev.run_task()) != "acknowledge_start":  # TCS EGSE ICD incorrectly says 'acknowledge_run_task'
        print(f"[red]ERROR: Starting the task failed: {response}[/]")
        end_observation()
        return

    # At this point all errors should be caught and we can end the observation and report the settings

    end_observation()

    if warning_msg:
        print("[orange3]Check if the value for the TRP1 setpoint in the configuration corresponds to your input.")

        cfg = tcs_dev.get_configuration()

        trp1_t_actual = float(cfg['ch1_tset'])
        print(f"TRP1 commanded setpoint = {temperature}, actual setpoint = {trp1_t_actual}")
    else:
        print(f"TRP1 setpoint set to {temperature:.2f}ºC.")


@exec_task(display_name="Set TRP1 setpoint and pmax")
def set_trp1_setpoint_and_pmax(temperature: float, pmax: float = 17500):
    """ Sets the TRP1 setpoint and maximum power.

    This pertains to the Ch1: TOU/TRP1 temperature sensors:
        - TOU_RTD1
        - TOU_RTD2
        - TOU_RTD3

    Args:
        - temperature: Temperature setpoint for TRP1 [°C].
        - pmax: the maximum power for TRP1 [default=17500].
    """

    warning_msg = False  # print a warning message at the end of the task

    if temperature is None or not isinstance(temperature, (float, int)):
        print("[red]You must provide a temperature as a float or int.[/]")
        return

    if pmax is None or not isinstance(pmax, (float, int)):
        print("[red]You must provide a TRP1 max power as a float or int.[/]")
        return

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if not tcs_dev.is_remote_operation_active():
        print("[orange3]WARNING: TCS EGSE not in remote operation mode, activating remote operations..[/]")
        tcs_dev.request_remote_operation()

    obsid = start_observation(f"Set TRP1 setpoint={temperature:.2f}ºC, and pmax={pmax}.")
    print(f"Observation started: {obsid}")

    print("Stopping task...")
    response = tcs_dev.stop_task()
    if "remote_mode_not_active" in response:
        print("[red]ERROR: Remote mode still not activated, aborting.[/]")
        end_observation()
        return
    if "no_task_is_running" in response:
        print("[orange3]WARNING: No task was running while attempting to stop the task, continuing...[/]")

    print("waiting 5s ...")
    time.sleep(5.0)  # empirically determined sleep time of 5s

    print("Set extended operating mode...")
    if (response := tcs_dev.set_operating_mode(mode=OperatingMode.EXTENDED)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    print("Set TRP1 setpoint and pmax...")
    if (response := tcs_dev.set_parameter(name="ch1_pmax", value=pmax)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP1 PMAX failed: {response}[/]")
        end_observation()
        return
    if (response := tcs_dev.set_parameter(name="ch1_tset", value=temperature)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP1 SETPOINT failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        if "erroneous_configuration" in response:
            print("[orange3]WARNING: The TRP1 setpoint or pmax values have been corrected by the TCS EGSE.[/]")
            warning_msg = True
        else:
            print(f"[red]ERROR: Setting TRP1 setpoint or pmax failed: {response}[/]")
            end_observation()
            return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    if (response := tcs_dev.run_task()) != "acknowledge_start":  # TCS EGSE ICD incorrectly says 'acknowledge_run_task'
        print(f"[red]ERROR: Starting the task failed: {response}[/]")
        end_observation()
        return

    # At this point all errors should be caught and we can end the observation and report the settings

    end_observation()

    if warning_msg:
        print("[orange3]Check if the value for the TRP1 setpoint in the configuration corresponds to your input.")

        cfg = tcs_dev.get_configuration()

        trp1_t_actual = float(cfg['ch1_tset'])
        trp1_pmax_actual = float(cfg['ch1_pmax'])

        table = Table("Parameter Name", "Commanded", "Actual")
        table.add_row("TRP1 setpoint", f"{temperature}", f"{trp1_t_actual}")
        table.add_row("TRP1 pmax", f"{pmax:.2f}", f"{trp1_pmax_actual:.2f}")

        print("\n", table)  # the newline is to fix the bug of a separation between line 1 and 2

    else:
        print(f"TRP1 setpoint set to {temperature:.2f}ºC, pmax set to {pmax:.2f}.")


@exec_task(display_name="Set TRP1 and TRP22 setpoint and pmax")
def set_setpoints_and_pmax(trp1_temperature: float, trp22_temperature: float,
                             trp1_pmax: float = 17500, trp22_pmax: float = 12500):
    """ Sets the TRP1 and TRP22 setpoints and maximum power.

    This pertains to the Ch1: TOU/TRP1 temperature sensors:
        - TOU_RTD1
        - TOU_RTD2
        - TOU_RTD3

    and to the Ch2: FEE/TRP22 temperature sensors:
        - FEE_RTD1
        - FEE_RTD2
        - FEE_RTD3

    Args:
        - trp1_temperature: Temperature setpoint for TRP1 [°C].
        - trp22_temperature: Temperature setpoint for TRP22 [°C].
        - trp1_pmax: maximum power for TRP1  [default=17500]
        - trp22_pmax: maximum power for TRP22 [default=12500]
    """

    warning_msg = False  # print a warning message at the end of the task

    if trp1_temperature is None or not isinstance(trp1_temperature, (float, int)):
        print("[red]You must provide a TRP1 temperature as a float or int.[/]")
        return

    if trp1_pmax is None or not isinstance(trp1_pmax, (float, int)):
        print("[red]You must provide a TRP1 max power as a float or int.[/]")
        return

    if trp22_temperature is None or not isinstance(trp22_temperature, (float, int)):
        print("[red]You must provide a TRP22 temperature as a float or int.[/]")
        return

    if trp22_pmax is None or not isinstance(trp22_pmax, (float, int)):
        print("[red]You must provide a TRP22 max power as a float or int.[/]")
        return

    if not is_tcs_cs_active(timeout=0.5):
        print("[red]ERROR: The TCS Control Server is not reachable.[/]")
        return

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    if not tcs_dev.is_remote_operation_active():
        print("[orange3]WARNING: TCS EGSE not in remote operation mode, activating remote operations..[/]")
        tcs_dev.request_remote_operation()

    obsid = start_observation(
        f"Set TRP1 (T={trp1_temperature:.2f}ºC, pmax={trp1_pmax}) and "
        f"TRP22 (T={trp22_temperature:.2f}ºC, pmax={trp22_pmax})."
    )
    print(f"Observation started: {obsid}")

    print("Stopping task...")
    response = tcs_dev.stop_task()
    if "remote_mode_not_active" in response:
        print("[red]ERROR: Remote mode still not activated, aborting.[/]")
        end_observation()
        return
    if "no_task_is_running" in response:
        print("[orange3]WARNING: No task was running while attempting to stop the task, continuing...[/]")

    print("waiting 5s ...")
    time.sleep(5.0)  # empirically determined sleep time of 5s

    print("Set extended operating mode...")
    if (response := tcs_dev.set_operating_mode(mode=OperatingMode.EXTENDED)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        print(f"[red]ERROR: Set extended operating mode failed: {response}[/]")
        end_observation()
        return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    print("Set TRP1 and TRP22 setpoint and pmax...")
    if (response := tcs_dev.set_parameter(name="ch1_pmax", value=trp1_pmax)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP1 PMAX failed: {response}[/]")
        end_observation()
        return
    if (response := tcs_dev.set_parameter(name="ch1_tset", value=trp1_temperature)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP1 SETPOINT failed: {response}[/]")
        end_observation()
        return
    if (response := tcs_dev.set_parameter(name="ch2_pmax", value=trp22_pmax)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP22 PMAX failed: {response}[/]")
        end_observation()
        return
    if (response := tcs_dev.set_parameter(name="ch2_tset", value=trp22_temperature)) != "acknowledge_parameter_change":
        print(f"[red]ERROR: Setting TRP22 SETPOINT failed: {response}[/]")
        end_observation()
        return

    if (response := tcs_dev.commit()) != "acknowledge_commit":
        if "erroneous_configuration" in response:
            print("[orange3]WARNING: Some of the TRP1 or TRP2 parameter values have been corrected "
                  "by the TCS EGSE.[/]")
            warning_msg = True
        else:
            print(f"[red]ERROR: Setting TRP1 and TRP22 failed: {response}[/]")
            end_observation()
            return

    print("waiting 2s ...")
    time.sleep(2.0)  # empirically determined sleep time of 2s

    if (response := tcs_dev.run_task()) != "acknowledge_start":  # TCS EGSE ICD incorrectly says 'acknowledge_run_task'
        print(f"[red]ERROR: Starting the task failed: {response}[/]")
        end_observation()
        return

    # At this point all errors should be caught and we can end the observation and report the settings

    end_observation()

    if warning_msg:
        print("[orange3]Check if the values for TRP1 and TRP22 in the configuration correspond to your input.")

        cfg = tcs_dev.get_configuration()

        trp1_t_actual = float(cfg['ch1_tset'])
        trp1_pmax_actual = float(cfg['ch1_pmax'])
        trp22_t_actual = float(cfg['ch2_tset'])
        trp22_pmax_actual = float(cfg['ch2_pmax'])

        table = Table("Parameter Name", "Commanded", "Actual")
        table.add_row("TRP1 setpoint", f"{trp1_temperature}", f"{trp1_t_actual}")
        table.add_row("TRP1 pmax", f"{trp1_pmax:.2f}", f"{trp1_pmax_actual:.2f}")
        table.add_row("TRP22 setpoint", f"{trp22_temperature}", f"{trp22_t_actual}")
        table.add_row("TRP22 pmax", f"{trp22_pmax:.2f}", f"{trp22_pmax_actual:.2f}")

        print("\n", table)  # the newline is to fix the bug of a separation between line 1 and 2

    else:
        print(f"TRP1 setpoint={trp1_temperature}ºC, pmax={trp1_pmax}, TRP22 setpoint={trp22_temperature}ºC, pmax={trp22_pmax}.")
