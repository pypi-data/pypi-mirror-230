import rich
import time
from gui_executor.exec import exec_ui

from egse.dpu import DPUProxy
from egse.hk import get_housekeeping, HKError
from rich.console import Console
from rich.table import Table

UI_MODULE_DISPLAY_NAME = "3 — N-FEE"


@exec_ui(display_name="Reset N-FEE")
def n_fee_reset() -> str:
    """ Reset the N-FEE (not implemented yet)."""
    print("Resetting the N-FEE has not been implemented yet.")
    return "N-FEE has not been reset."


@exec_ui(display_name="Sync N-FEE Register Map")
def n_fee_sync_register_map(description: str = "DPU CS: Load and sync N-FEE Register Map",
                            on_long_pulse: bool = True) -> None:
    """
    Synchronise the Register Map between the N-FEE and the DPU Processor,
    then print all register values.

    Args:
        description: info message for the observation log
        on_long_pulse: execute the sync request just before the next long pulse
    """
    from camtest import start_observation, end_observation, GlobalState
    from camtest.commanding import dpu
    from egse.dpu import DPUInterface

    dpu_dev: DPUInterface = GlobalState.setup.camera.dpu.device

    start_observation(description=description)

    if on_long_pulse:
        rich.print("When in external sync mode, this command can take up to 25s..", flush=True)
        reg_map = dpu.on_frame_number_do(3 if dpu.n_cam_is_ext_sync() else 0, dpu_dev.n_fee_sync_register_map)
    else:
        reg_map = dpu_dev.n_fee_sync_register_map()

    end_observation()

    rich.print(reg_map)


@exec_ui(display_name="To ON mode")
def n_fee_to_on_mode(description: str = "CAM switch on: FEE to ON MODE") -> str:
    """ Bring the N-FEE to on mode.

    This task waits until the N-FEE is in on mode, which can take up to 25s.
    """

    from camtest import start_observation, end_observation, load_setup
    from camtest.commanding import dpu

    load_setup()

    start_observation(description=description)

    dpu.n_cam_to_on_mode()
    print("Wait until the N-FEE is in ON mode, this can take up to 25s.", flush=True)
    while not dpu.n_cam_is_on_mode():
        time.sleep(1.0)
    end_observation()

    print("N-FEE in ON mode.")


@exec_ui(display_name="To STANDBY mode")
def n_fee_to_standby_mode(description: str = "CAM switch on: FEE to STANDBY MODE") -> str:
    """ Bring the N-FEE to stand-by mode.

    This task waits until the N-FEE is in stand-by mode, which can take up to 25s.
    """
    from camtest import start_observation, end_observation, load_setup
    from camtest.commanding import dpu

    load_setup()

    start_observation(description=description)

    dpu.n_cam_to_standby_mode()
    print("Wait until the N-FEE is in STANDBY mode, this can take up to 25s.", flush=True)
    while not dpu.n_cam_is_standby_mode():
        time.sleep(1.0)
    end_observation()

    print("N-FEE in STANDBY mode.")


@exec_ui(display_name="To DUMP mode")
def n_fee_to_dump_mode(description: str = "CAM switch on: FEE to DUMP MODE", int_sync: bool = False) -> str:
    """ Bring the N-FEE to dump mode.

    This task waits until the N-FEE is in dump mode, which can take up to 25s.
    """
    from camtest import start_observation, end_observation, load_setup
    from camtest.commanding import dpu

    load_setup()

    description = f"{description} — {'internal' if int_sync else 'external'} sync"
    start_observation(description=description)

    dpu.n_cam_to_dump_mode_int_sync() if int_sync else dpu.n_cam_to_dump_mode()
    print("Wait until the N-FEE is in DUMP mode, this can take up to 25s.", flush=True)
    while not dpu.n_cam_is_dump_mode():
        time.sleep(1.0)

    while not (dpu.n_cam_is_int_sync() if int_sync else dpu.n_cam_is_ext_sync()):
        time.sleep(1.0)

    end_observation()

    print("N-FEE in DUMP mode.")


@exec_ui(display_name="Set FPGA defaults")
def n_fee_set_fpga_defaults():
    """ Set the FPGA defaults in the N-FEE register map.

    The new FPGA default values are read from the setup (setup.camera.fee.fpga_defaults).
    """

    from camtest import start_observation, end_observation, load_setup
    from camtest.commanding import dpu

    load_setup()

    start_observation(description="Setting the FPGA defaults in the FEE register map")
    dpu.n_fee_set_fpga_defaults()
    end_observation()


@exec_ui(display_name="Print register map", immediate_run=True)
def print_register_map():
    """
    Fetches the RegisterMap from the DPU Processor, then prints all register values.
    This task doesn't communicate with the N-FEE, but fetches the RegisterMap from the DPU Processor.
    There is no synchronisation of the memory map at this point. If you need to synchronise the N-FEE
    RegisterMap on the DPU Processor, use the 'Sync N-FEE Register Map' task.
    """
    with DPUProxy() as proxy:
        rich.print(proxy.get_register_map())


@exec_ui(display_name="CCD Temperatures and N-FEE Voltages")
def print_ccd_temperatures_and_nfee_voltages():
    """ Print the calibration CCD temperatures and N-FEE voltages.

    This task prints out a table with the calibrated CCD temperatures and the calibrated voltages, supplied by the
    N-FEE.  The values are taken from the N-FEE HK.
    """

    table = Table(title="CCD Temperatures & N-FEE Voltages")
    table.add_column("Parameter")
    table.add_column("Value", justify="right")

    parameter_names = ["NFEE_T_CCD1", "NFEE_T_CCD2", "NFEE_T_CCD3", "NFEE_T_CCD4", "NFEE_VCCD_R", "NFEE_VCLK_R",
                       "NFEE_VAN1_R", "NFEE_VAN2_R", "NFEE_VAN3_R", "NFEE_VDIG"]

    for parameter_name in parameter_names:
        unit = "°C" if "_T_" in parameter_name else "V"

        try:
            _, value = get_housekeeping(parameter_name)
            value = f'{float(value):.5f}'
            table.add_row(f"{parameter_name} [{unit}]", value)
        except HKError:
            table.add_row(f"{parameter_name} [{unit}]", "NA")

    console = Console(width=120)
    console.print(table)
