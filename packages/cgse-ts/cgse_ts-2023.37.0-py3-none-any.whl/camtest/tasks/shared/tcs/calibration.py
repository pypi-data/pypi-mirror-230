import time
from pathlib import Path

from gui_executor.exec import exec_ui
from rich import print
from rich.console import Console
from rich.table import Table

from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState
from egse.tcs import OperatingMode
from egse.tcs.tcs import TCSInterface, ClosedLoopMode

UI_MODULE_DISPLAY_NAME = "1 - Calibration"

ICON_PATH = Path(__file__).parent.resolve() / "icons"


@exec_ui(display_name="Set PI Control Loop parameters", input_request=("? [Y/n]",))
def set_pi_control_loop_parameters(
        ch1_ki: float = 0.0772,
        ch1_kp: float = 40.9651,
        ch1_pmax: int = 17500,
        ch2_ki: float = 0.0001,
        ch2_kp: float = 1.0,
        ch2_pmax: int = 12500,
):
    """ Set the TCS PI control loop parameters for both channels.

    Args:
        - ch1_ki: Integral gain to use for Ch1 (TOU/TRP1)
        - ch1_kp: Principal gain to use for Ch1 (TOU/TRP1)
        - ch1_pmax: Maximum power delivered to the heater for Ch1 (TOU/TRP1) [mW]
        - ch2_ki: Integral gain to use for Ch2 (FEE/TRP22)
        - ch2_kp: Principal gain to use for Ch2 (FEE/TRP22)
        - ch2_pmax: Maximum power delivered to the heater for Ch2 (FEE/TRP22) [mW]
    """

    from camtest.commanding import tcs

    tcs_dev: TCSInterface = GlobalState.setup.gse.tcs.device

    start_observation("Setup TCS EGSE: Configure PI control parameters.")
    tcs.stop_task()
    time.sleep(5.0)
    tcs.set_operating_mode(mode=OperatingMode.EXTENDED)
    tcs.set_closed_loop_mode(channel='ch1', mode=ClosedLoopMode.PI_ALG_1)
    tcs.set_closed_loop_mode(channel='ch2', mode=ClosedLoopMode.PI_ALG_2)
    tcs.set_pi_parameters(channel='ch1', ki=ch1_ki, kp=ch1_kp, pmax=ch1_pmax)
    tcs.set_pi_parameters(channel='ch2', ki=ch2_ki, kp=ch2_kp, pmax=ch2_pmax)

    # check the values in the TCS GUI before proceeding

    conf = tcs_dev.get_configuration()

    table = Table(title="TCS PI Control Loop Parameters")

    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="green")

    for name, value in sorted(
            {
                x: conf[x] for x in ("ch1_pi_parameters_ki", "ch1_pi_parameters_kp", "ch1_pmax",
                                     "ch2_pi_parameters_ki", "ch2_pi_parameters_kp", "ch2_pmax")
            }.items()
    ):
        table.add_row(name, value)

    console = Console(width=120)
    console.print(table)

    rc = input("Are the PI Control Loop parameters correctly configured? [Y/n]")
    if rc.lower() != 'y':
        print("Fix parameters before proceeding.")
        end_observation()
        return

    tcs.set_operating_mode(mode=OperatingMode.CALIBRATION)
    tcs.start_task()
    end_observation()


@exec_ui(display_name="Load RTD Calibration")
def load_rtd_calibration():
    """ Load the RTD calibration into the TCS unit.

    The calibration coefficients are read from the setup.
    """

    from camtest.commanding import tcs

    try:
        start_observation("Configure TCS EGSE: load TRP1 and TRP22 sensor calibration")
        tcs.load_rtd_calibration()
    finally:
        end_observation()
