from pathlib import Path
from typing import List

from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback
from rich.console import Console
from rich.table import Table

from camtest import end_observation
from camtest import start_observation
from camtest.commanding import aeu
from camtest.commanding.aeu import reconnect
from camtest.tasks.shared.camera import environments
from egse.aeu.aeu import AWGInterface
from egse.aeu.aeu import AWG_ERRORS
from egse.aeu.aeu import CRIOInterface
from egse.aeu.aeu import CRIO_ERRORS
from egse.aeu.aeu import CURRENT_QUALITY
from egse.aeu.aeu import IntSwitch
from egse.aeu.aeu import PSUInterface
from egse.aeu.aeu import SyncData
from egse.aeu.aeu import VOLTAGE_QUALITY
from egse.dpu import DPUInterface
from egse.fee import n_fee_mode
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "2 — AEU"

ICON_PATH = Path(__file__).parent.resolve() / "icons/"


def image_cycle_times() -> List:
    """ Returns list of allowed image cycle times (for the N-cam).

    This list is composed of the information in the setup (i.c. the calibration of the AEU AWG2).  If this information
    is not present in the setup, a default list is returned.

    Returns: List of allowed image cycle times (for the N-cam) [s].
    """
    try:
        awg2_setup = GlobalState.setup.gse.aeu.awg2.calibration.n_cam_sync_data
        return [SyncData(awg2_setup[key]).image_cycle_time for key in awg2_setup.keys()]
    except AttributeError:
        return [25.0, 31.25, 37.5, 43.75, 50]


@exec_ui(display_name="Switch ON",
         icons=(ICON_PATH / "aeu-on.svg", ICON_PATH / "aeu-on-selected.svg"))
def switch_on_aeu(image_cycle_time: Callback(image_cycle_times, name="float"), svm_nom: IntSwitch = IntSwitch.ON,
                  svm_red: IntSwitch = IntSwitch.OFF):
    """ N-AEU switch-on.

    This task enables the six power lines (CCD, CLK, AN1, AN2, AND3, and DIG) and enables the sync signals
    (Clk_50MHz, Clk_ccdread, and the nominal and/or redundant SVM clocks).  This way, the N-FEE is powered on and can be
    operated in external sync.

    Args:
        - image_cycle_time: Image cycle time (the time between two subsequent long sync pulses) [s].
        - svm_nom: Whether the nominal SVM clocks (Clk_heater and Clk_50Hz) should be enabled.
        - svm_red: Whether the redundant SVM clocks (Clk_heater and Clk_50MHz) should be enabled.
    """

    try:
        start_observation("AEU switch-on")
        aeu.n_cam_swon()
        aeu.n_cam_sync_enable(image_cycle_time=image_cycle_time, svm_nom=svm_nom, svm_red=svm_red)
    finally:
        end_observation()


@exec_ui(display_name="Switch OFF",
         icons=(ICON_PATH / "aeu-off.svg", ICON_PATH / "aeu-off-selected.svg"),)
def switch_off_aeu():
    """ N-AEU switch-off.

    This task disables all sync signals and the six power lines (CCD, CLK, AN1, AN2, AND3, and DIG). This way, the
    N-FEE is powered off.
    """

    try:
        start_observation("AEU switch-off")
        aeu.n_cam_sync_disable()
        aeu.n_cam_swoff()
    finally:
        end_observation()


@exec_ui(display_name="Power consumption")
def print_power_consumption(environment: Callback(environments, name="Test environment") = None):
    """ Print the AEU cRIO voltages and currents.

    This task prints out a table with the AEU cRIO voltages and currents.  For the voltages, the nominal values
    (together with the tolerances) are printed out.  Any non-nominal voltages are shown in red.

    Below the table it is reported whether the voltages are nominal, and - if not - which voltages are not in the
    nominal range.

    Args:
        - environment: Indicates whether testing at ambient or under TVAC (relevant for the power consumption checks)
    """
    from egse.hk import read_conversion_dict
    from egse.hk import convert_hk_names

    setup = GlobalState.setup

    from egse.dpu.dpu_cs import is_dpu_cs_active
    if not is_dpu_cs_active():
        print("The DPU CS must be active for the power consumption checks")
        return 

    dpu_if: DPUInterface = GlobalState.setup.camera.dpu.device
    operating_mode = n_fee_mode(dpu_if.n_fee_get_mode())

    try:
        nominal_voltages = setup.camera.fee.power_consumption.voltages
    except AttributeError:
        nominal_voltages = None
    try:
        nominal_currents_all_modes = setup.camera.fee.power_consumption.currents

        if operating_mode == n_fee_mode.ON_MODE:
            nominal_currents = nominal_currents_all_modes.on_mode
        elif operating_mode == n_fee_mode.STAND_BY_MODE:
            nominal_currents = nominal_currents_all_modes.standby_mode
        elif operating_mode == n_fee_mode.FULL_IMAGE_MODE:
            nominal_currents = nominal_currents_all_modes.full_image_mode_integration
            nominal_currents.pop("GAEU_I_CLK_NFEE")
            nominal_currents.pop("GAEU_I_AN1_NFEE")
            nominal_currents.pop("GAEU_I_DIG_NFEE")
        else:
            nominal_currents = None
    except AttributeError:
        nominal_currents = None

    try:
        if environment == "ambient":
            nominal_power_all_modes = setup.camera.fee.power_consumption.power.ambient
        elif environment == "TVAC":
            nominal_power_all_modes = setup.camera.fee.power_consumption.power.tvac

        if operating_mode == n_fee_mode.ON_MODE:
            nominal_powers = nominal_power_all_modes.on_mode
        elif operating_mode == n_fee_mode.STAND_BY_MODE:
            nominal_powers = nominal_power_all_modes.standby_mode
        elif operating_mode == n_fee_mode.FULL_IMAGE_MODE:
            nominal_powers = nominal_power_all_modes.full_image_mode_integration
            nominal_powers.pop("GAEU_I_CLK_NFEE")
            nominal_powers.pop("GAEU_I_AN1_NFEE")
            nominal_powers.pop("GAEU_I_DIG_NFEE")
        else:
            nominal_powers = None
    except AttributeError:
        nominal_powers = None

    try:

        crio: CRIOInterface = setup.gse.aeu.crio.device
        reconnect(crio)

        crio_data = crio.get_data()

        hk_conversion_table = read_conversion_dict("AEU-CRIO", use_site=False)
        crio_data = convert_hk_names(crio_data, hk_conversion_table)

        voltage_names = ["GAEU_V_CCD_NFEE", "GAEU_V_CLK_NFEE", "GAEU_V_AN1_NFEE", "GAEU_V_AN2_NFEE", "GAEU_V_AN3_NFEE",
                         "GAEU_V_DIG_NFEE"]
        current_names = ["GAEU_I_CCD_NFEE", "GAEU_I_CLK_NFEE", "GAEU_I_AN1_NFEE", "GAEU_I_AN2_NFEE", "GAEU_I_AN3_NFEE",
                         "GAEU_I_DIG_NFEE"]
        power_names = ["GAEU_P_CCD_NFEE", "GAEU_P_CLK_NFEE", "GAEU_P_AN1_NFEE", "GAEU_P_AN2_NFEE", "GAEU_P_AN3_NFEE",
                       "GAEU_P_DIG_NFEE"]

        table = Table(title=f"Power consumption ({operating_mode.name})")
        table.add_column("Parameter")
        table.add_column("Value", justify="right")
        table.add_column("Nominal range", justify="right", footer="Values taken from setup")
        table.add_column("OK/NOK", justify="right")

        not_all_in_range = False
        not_all_ranges_defined = False

        # Voltage

        for voltage_name in voltage_names:
            measured_voltage = crio_data[voltage_name]

            if nominal_voltages:
                nominal_voltage, voltage_tolerance = nominal_voltages[voltage_name]

                if nominal_voltage - voltage_tolerance <= measured_voltage <= nominal_voltage + voltage_tolerance:
                    color = "black"
                    ok_nok = "OK"
                else:
                    color = "red"
                    ok_nok = "NOK"
                    not_all_in_range = True

                table.add_row(f"{voltage_name} [ V ]", str(measured_voltage),
                              f"{nominal_voltage} +/- {voltage_tolerance}", ok_nok, style=color)
            else:
                not_all_ranges_defined = True
                table.add_row(f"{voltage_name} [ V ]", str(measured_voltage), style="#FFA500")

        # Current

        for current_name in current_names:
            measured_current = crio_data[current_name] * 1000   # Conversion A -> mA

            if nominal_currents and current_name in nominal_currents:
                nominal_current, percentage = nominal_currents[current_name]
                current_tolerance = percentage * abs(nominal_current) / 100.

                if nominal_current - current_tolerance <= measured_current <= nominal_current + current_tolerance:
                    color = "black"
                    ok_nok = "OK"
                else:
                    color = "red"
                    not_all_in_range = True
                    ok_nok = "NOK"

                table.add_row(f"{current_name} [ mA ]", str(measured_current), f"{nominal_current} +/- {percentage}%", 
                              ok_nok, style=color)
            else:
                not_all_ranges_defined = True
                table.add_row(f"{current_name} [ mA ]", str(measured_current), style="#FFA500")

        # Power

        for voltage_name, current_name, power_name in zip(voltage_names, current_names, power_names):

            measured_power = crio_data[voltage_name] * crio_data[current_name]
            if nominal_powers and power_name in nominal_powers:
                nominal_power, percentage = nominal_powers[power_name]
                power_tolerance = percentage * nominal_power

                if nominal_power - power_tolerance <= measured_power <= nominal_power + power_tolerance:
                    color = "black"
                    ok_nok = "OK"
                else:
                    color = "red"
                    ok_nok = "NOK"
                    not_all_in_range = True
                table.add_row(f"{power_name} [ W ]", f"{measured_power:.5f}", f"{nominal_power} +/- {percentage}%", 
                              ok_nok, style=color)
            else:
                not_all_ranges_defined = True
                table.add_row(f"{power_name} [ W ]", f"{measured_power:.5f}", style="#FFA500")

        console = Console(width=200)
        console.print(table)

        if not_all_in_range:
            print("Not all voltage/current/power values are within their nominal range (these are highlighted in red).")
        if not_all_ranges_defined:
            print("Nominal ranges have not been defined for all voltage/current/power values (these are highlighted in "
                  "orange).")
    except NotImplementedError:
        print("No connection could be established to the AEU cRIO.")


@exec_ui(display_name="Generate AEU report")
def generate_aeu_report():
    """Generate report on the status of the AEU.

    A table will be printed, reporting on the following information:
        - Voltage quality of the six power lines (CCD, CLK, AN1, AN2, AND3, and DIG).  By voltage quality we mean:
          whether the voltages are in-range, or an over- or under-voltage protection was triggered.
        - Current quality of the six power lines (CCD, CLK, AN1, AN2, AND3, and DIG).  By current quality we mean:
          whether the currents are in-range or an over-current protection was triggered;
        - Synchronisation status of Clk_50MHz;
        - Synchronisation status of Clk_ccdread;
        - Synchronisation status of the nominal Clk_heater_50MHz;
        - Synchronisation status of redundant Clk_heater_50MHz;
        - Synchronisation status of the nominal Clk_heater;
        - Synchronisation status of the redundant Clk_heater;
        - Status of the N-FEE clocks;
        - Status of the heater clocks
        - Error state of the cRIO;
        - Error state of the six Power Supply Units (PSU);
        - Query state of the two Arbitrary Wave Generators (AWG)
        - Execution state of the two Arbitrary Wave Generators (AWG).
    """

    setup = GlobalState.setup

    table = Table(title="AEU Status Report")
    table.add_column("Parameter")
    table.add_column("Status", no_wrap=True)

    try:
        # Voltage quality

        crio: CRIOInterface = setup.gse.aeu.crio.device
        reconnect(crio)

        v_ccd_quality, v_clk_quality, v_an1_quality, v_an2_quality, v_an3_quality, v_dig_quality = \
            crio.get_n_cam_voltage_quality()

        voltage_quality_style = ["black", "red", "red"]
        table.add_row("V_CCD voltage", str(VOLTAGE_QUALITY[v_ccd_quality]), style=voltage_quality_style[v_ccd_quality])
        table.add_row("V_CLK voltage", str(VOLTAGE_QUALITY[v_clk_quality]), style=voltage_quality_style[v_clk_quality])
        table.add_row("V_AN1 voltage", str(VOLTAGE_QUALITY[v_an1_quality]), style=voltage_quality_style[v_an1_quality])
        table.add_row("V_AN2 voltage", str(VOLTAGE_QUALITY[v_an2_quality]), style=voltage_quality_style[v_an2_quality])
        table.add_row("V_AN3 voltage", str(VOLTAGE_QUALITY[v_an3_quality]), style=voltage_quality_style[v_an3_quality])
        table.add_row("V_DIG voltage", str(VOLTAGE_QUALITY[v_dig_quality]), style=voltage_quality_style[v_dig_quality])

        # Current quality

        i_ccd_quality, i_clk_quality, i_an1_quality, i_an2_quality, i_an3_quality, i_dig_quality = \
            crio.get_n_cam_current_quality()

        current_quality_style = ["black", "red"]
        table.add_row("V_CCD current", str(CURRENT_QUALITY[i_ccd_quality]), style=current_quality_style[i_ccd_quality])
        table.add_row("V_CLK current", str(CURRENT_QUALITY[i_clk_quality]), style=current_quality_style[i_clk_quality])
        table.add_row("V_AN1 current", str(CURRENT_QUALITY[i_an1_quality]), style=current_quality_style[i_an1_quality])
        table.add_row("V_AN2 current", str(CURRENT_QUALITY[i_an2_quality]), style=current_quality_style[i_an2_quality])
        table.add_row("V_AN3 current", str(CURRENT_QUALITY[i_an3_quality]), style=current_quality_style[i_an3_quality])
        table.add_row("V_DIG current", str(CURRENT_QUALITY[i_dig_quality]), style=current_quality_style[i_dig_quality])

        # N-FEE clock status

        clk_50mhz_status, clk_ccdread_status = crio.get_n_cam_clock_quality()

        if clk_50mhz_status:
            table.add_row("Clk_50MHz synchronisation status", "Synchronisation failure detected", style="red")
        else:
            table.add_row("Clk_50MHz synchronisation status", "No synchronisation failure detected")
        if clk_ccdread_status:
            table.add_row("Clk_ccdread synchronisation status", "Synchronisation failure detected", style="red")
        else:
            table.add_row("Clk_ccdread synchronisation status", "No synchronisation failure detected")

        # Heater clock status

        clk_50mhz_nom_status, clk_50mhz_red_status, clk_heater_nom, clk_heater_red = crio.get_svm_clock_quality()

        if clk_50mhz_nom_status:
            table.add_row("Nominal Clk_heater_50MHz synchronisation status", "Synchronisation failure detected", style="red")
        else:
            table.add_row("Nominal Clk_heater_50MHz synchronisation status", "No synchronisation failure detected")

        if clk_50mhz_red_status:
            table.add_row("Redundant Clk_heater_50MHz synchronisation status", "Synchronisation failure detected", style="red")
        else:
            table.add_row("Redundant Clk_heater_50MHz synchronisation status", "No synchronisation failure detected")

        if clk_heater_nom:
            table.add_row("Nominal Clk_heater synchronisation status", "Synchronisation failure detected",
                          style="red")
        else:
            table.add_row("Nominal Clk_heater synchronisation status", "No synchronisation failure detected")

        if clk_50mhz_red_status:
            table.add_row("Redundant Clk_heater synchronisation status", "Synchronisation failure detected",
                          style="red")
        else:
            table.add_row("Redundant Clk_heater synchronisation status", "No synchronisation failure detected")

        # cRIO error state

        crio_error = crio.get_error_info()

        crio_error_style = ["black"] + 6 * ["red"]
        table.add_row("cRIO error state", CRIO_ERRORS[crio_error], style=crio_error_style[crio_error])

    except NotImplementedError:
        table.add_row("cRIO error state", "Control server down", style="red")

    # PSU error state

    for index in range(1, 7):
        try:
            psu: PSUInterface = setup.gse.aeu[f"psu{index}"]["device"]
            reconnect(psu)

            psu_error = psu.get_error_info()
            table.add_row(f"PSU{index} error state", f"{psu_error[1]} ({psu_error[0]})")
        except NotImplementedError:
            table.add_row(f"PSU{index} error state", "Control server down", style="red")

    # AWG error state

    for index in range(1, 3):
        try:
            awg: AWGInterface = setup.gse.aeu[f"awg{index}"]["device"]
            reconnect(awg)

            awg_query_error = awg.query_error_register()
            awg_execution_error = awg.execution_error_register()

            try:
                table.add_row(f"AWG{index} query error state", f"{AWG_ERRORS[awg_query_error]} ({awg_query_error})")
            except KeyError:
                table.add_row(f"AWG{index} query error state", "No errors")
            try:
                table.add_row(f"AWG{index} execution error state", f"{AWG_ERRORS[awg_execution_error]} ({awg_execution_error})")
            except KeyError:
                table.add_row(f"AWG{index} execution error state", "No errors")
        except NotImplementedError:
            table.add_row(f"AWG{index} error state", "Control server down", style="red")

    console = Console(width=120)
    console.print(table)
