import logging
import string
import time

from camtest.core.exec import building_block
from egse.aeu import aeu_metrics
from egse.aeu.aeu import ARB, SELFTEST_RESULT, LOOPBACK, VOLTAGE_QUALITY, CURRENT_QUALITY, ArbData
from egse.aeu.aeu import AWGInterface
from egse.aeu.aeu import CRIOInterface
from egse.aeu.aeu import CRIOProxy
from egse.aeu.aeu import IntSwitch
from egse.aeu.aeu import LoopBack
from egse.aeu.aeu import OperatingMode
from egse.aeu.aeu import PSUInterface
from egse.aeu.aeu import PSUProxy
from egse.aeu.aeu import PriorityMode
from egse.aeu.aeu import Switch
from egse.aeu.aeu import SyncData
from egse.aeu.aeu import Waveform
from egse.aeu.aeu_devif import AEUError
from egse.state import GlobalState
from egse.system import wait_until

VOLTAGES = ["V_CCD", "V_CLK", "V_AN1", "V_AN2", "V_AN3", "V_DIG"]
NUM_POWERLINES = 6
N_CAM_CLK = ["Clk_50MHz", "Clk_ccdread"]
F_CAM_CLK = ["Clk_50MHz_nom", "Clk_50MHz_red", "Clk_ccdread_nom", "Clk_ccdread_red"]
TCS_CLK = ["Clk_50MHz_nom", "Clk_50MHz_red", "Clk_heater_nom", "Clk_heater_red"]
NUM_CLK_N_CAM = 2
NUM_CLK_F_CAM = 4
NUM_CLK_TCS = 4

LOGGER = logging.getLogger(__name__)

##################################
# Confirm the status of the camera
##################################


def reconnect(*interfaces):
    """ Reconnect to the given interfaces.

    Some of the AEU devices seem to time out after a while and in order to be able to command them again, you must
    explicitly re-connect to the device.

    This method must be called at the very start of each of the methods in this module.
    """

    for interface in interfaces:

        interface.reconnect()


def n_cam_is_on():
    """ Check whether the N-CAM is powered on.

    This is the case if:

        - the six PSUs have been switched on;
        - the secondary power lines for the N-CAM have been switched on.

    Returns: True of the N-CAM is powered on; False otherwise.
    """

    # return get_housekeeping("GAEU_PWR_NFEE_STATUS") == 1 and get_housekeeping("GAEU_PWR_CCD_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_CLK_FEE_STATUS") == 1 and get_housekeeping("GAEU_PWR_AN1_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_AN2_FEE_STATUS") and get_housekeeping("GAEU_PWR_AN3_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_DIG_FEE_STATUS") == 1

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device

    if not crio.ping():

        return False

    led_status = crio.get_led_status()

    return led_status["N-CAM"] and led_status["V_CCD"] and led_status["V_CLK"] and led_status["V_AN1"] \
        and led_status["V_AN2"] and led_status["V_AN3"] and led_status["V_DIG"]


def f_cam_is_on():
    """ Check whether the F-CAM is powered on.

    This is the case if:

        - the six PSUs have been switched on;
        - the secondary power lines for the F-CAM have been switched on.

    Returns: True of the F-CAM is powered on; False otherwise.
    """

    # return get_housekeeping("GAEU_PWR_FFEE_STATUS") == 1 and get_housekeeping("GAEU_PWR_CCD_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_CLK_FEE_STATUS") == 1 and get_housekeeping("GAEU_PWR_AN1_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_AN2_FEE_STATUS") and get_housekeeping("GAEU_PWR_AN3_FEE_STATUS") == 1 \
    #     and get_housekeeping("GAEU_PWR_DIG_FEE_STATUS") == 1

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device

    if not crio.ping():

        return False

    led_status = crio.get_led_status()

    return led_status["F-CAM"] and led_status["V_CCD"] and led_status["V_CLK"] and led_status["V_AN1"] \
        and led_status["V_AN2"] and led_status["V_AN3"] and led_status["V_DIG"]


def n_cam_is_syncing():
    """ Check whether the AEU is sending the N-CAM sync signals.

    This is the case if the following sync signals are being sent:

        - Clk_50MHz;
        - Clk_ccdread;
        - Clk_heater (nominal or redundant).

    Returns: True of the AEU is sending the N-CAM sync signals; False otherwise.
    """

    # return get_housekeeping("GAEU_CLK_PWR_50MHZ") == 1 and get_housekeeping("GAEU_CLK_PWR_CCDREAD") == 1 \
    #     and get_housekeeping("GAEU_CLK_PWR_SVM") == 1

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device

    if not crio.ping():

        return False

    led_status = crio.get_led_status()

    return led_status["Clk_50MHz"] and led_status["Clk_ccdread"] and led_status["Clk_heater"]


def f_cam_is_syncing():
    """ Check whether the AEU is sending the F-CAM sync signals.

    This is the case if the following sync signals are being sent:

        - Clk_50MHz;
        - Clk_ccdread_nom or Clk_ccdread_red;
        - Clk_heater (nominal or redundant).
    """

    # return get_housekeeping("GAEU_CLK_PWR_50MHZ") == 1 and get_housekeeping("GAEU_CLK_PWR_CCDREAD") == 1 \
    #     and get_housekeeping("GAEU_CLK_PWR_SVM") == 1 \
    #     and (get_housekeeping("GAEU_CLK_PWR_N_FFEE") or get_housekeeping("GAEU_CLK_PWR_R_FFEE"))

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device

    if not crio.ping():

        return False

    # reconnect(crio)

    led_status = crio.get_led_status()

    return led_status["Clk_50MHz"] and led_status["Clk_ccdread"] and led_status["Clk_heater"] and \
        (led_status["Clk_F_FEE_N"] or led_status["Clk_F_FEE_R"])


def confirm_n_cam_status():
    """ Confirm the status of the N-CAM.

    The following items are checked:

        - Operating mode;
        - PSU output status;
        - N-CAM secondary power lines;
        - Measured N-CAM voltages;
        - Measured N-CAM currents;
        - Status of the N-CAM clocks;
        - Status of the SVM clocks.
    """

    LOGGER.info("Confirming the N-CAM status")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(crio, psu1, psu2, psu3, psu4, psu5, psu6)

    # 1. Check the actual operating mode

    LOGGER.info(f"Operating mode: {crio.get_operating_mode()}")

    # 2. Check the output status of PSU 1

    LOGGER.info(f"Output status of PSU1: {psu1.get_output_status()}")

    # 3. Check the output status of PSU 2

    LOGGER.info(f"Output status of PSU2: {psu2.get_output_status()}")

    # 4. Check the output status of PSU 3

    LOGGER.info(f"Output status of PSU3: {psu3.get_output_status()}")

    # 5. Check the output status of PSU 4

    LOGGER.info(f"Output status of PSU4: {psu4.get_output_status()}")

    # 6. Check the output status of PSU 5

    LOGGER.info(f"Output status of PSU5: {psu5.get_output_status()}")

    # 7. Check the output status of PSU 6

    LOGGER.info(f"Output status of PSU6: {psu6.get_output_status()}")

    # 8. Check the secondary power lines

    LOGGER.info(f"Secondary power lines of N-CAM: {crio.get_n_cam_secondary_power_status()}")

    # 9. Measure the voltage values in N-CAM

    LOGGER.info(f"Measured voltages in N-CAM: {crio.get_n_cam_voltage()}")

    # 10. Measure the current values in N-CAM

    LOGGER.info(f"Measured currents in N-CAM: {crio.get_n_cam_current()}")

    # 11. Check the status of the N-CAM clocks

    LOGGER.info(f"Status of the N-CAM clocks: {crio.get_n_cam_clock_status()}")

    # 11. Check the status of the SVM clocks

    LOGGER.info(f"Status of the SVM clocks: {crio.get_svm_clock_status()}")


def confirm_f_cam_status():
    """ Confirm the status of the N-CAM.

    The following items are checked:

        - Operating mode;
        - PSU output status;
        - F-CAM secondary power lines;
        - Measured F-CAM voltages;
        - Measured F-CAM currents;
        - Status of the F-CAM clocks;
        - Status of the SVM clocks.
    """

    LOGGER.info("Confirming the F-CAM status")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(crio, psu1, psu2, psu3, psu4, psu5, psu6)

    # 1. Check the actual operating mode

    LOGGER.info(f"Operating mode: {crio.get_operating_mode()}")

    # 2. Check the output status of PSU 1

    LOGGER.info(f"Output status of PSU1: {psu1.get_output_status()}")

    # 3. Check the output status of PSU 2

    LOGGER.info(f"Output status of PSU2: {psu2.get_output_status()}")

    # 4. Check the output status of PSU 3

    LOGGER.info(f"Output status of PSU3: {psu3.get_output_status()}")

    # 5. Check the output status of PSU 4

    LOGGER.info(f"Output status of PSU4: {psu4.get_output_status()}")

    # 6. Check the output status of PSU 5

    LOGGER.info(f"Output status of PSU5: {psu5.get_output_status()}")

    # 7. Check the output status of PSU 6

    LOGGER.info(f"Output status of PSU6: {psu6.get_output_status()}")

    # 8. Check the secondary power lines

    LOGGER.info(f"Secondary power lines of F-CAM: {crio.get_f_cam_secondary_power_status()}")

    # 9. Measure the voltage values in F-CAM

    LOGGER.info(f"Measured voltages in F-CAM: {crio.get_f_cam_voltage()}")

    # 10. Measure the current values in F-CAM

    LOGGER.info(f"Measured currents in F-CAM: {crio.get_f_cam_current()}")

    # 11. Check the status of the F-CAM clocks

    LOGGER.info(f"Status of the F-CAM clocks: {crio.get_f_cam_clock_status()}")

    # 11. Check the status of the SVM clocks

    LOGGER.info(f"Status of the SVM clocks: {crio.get_svm_clock_status()}")


######################
# Switch on the camera
######################


@building_block
def n_cam_swon():
    """ Power on N-CAM.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).
    """

    LOGGER.info("Switch on the N-CAM")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    crio_cal = setup.gse.aeu.crio.calibration
    reconnect(crio)

    # This command is only supposed to be executed when both the N- and the F-CAM were powered off

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]
    f_cam_powered = crio_data["F-CAM"]

    if n_cam_powered:

        raise AEUError("N-CAM already powered on")

    if f_cam_powered:

        raise AEUError("F-CAM already powered on")

    # 1. Change the operating mode to "Functional & TVAC Operating Mode"

    crio.set_operating_mode(OperatingMode.FC_TVAC)

    # 2. Check the actual operating mode

    operating_mode = crio.get_operating_mode()

    LOGGER.info(f"Operating mode: {operating_mode} ({OperatingMode(operating_mode).name})")

    if operating_mode != OperatingMode.FC_TVAC:

        raise AEUError(f"The current operating mode ({operating_mode}) should be FC_TVAC")

    # 2.5 Configure the start-up and trip timings for the protection values.

    timings = [*crio_cal.n_cam_ovp_t_t, *crio_cal.f_cam_ovp_t_t, *crio_cal.n_cam_uvp_t_t,
               *crio_cal.f_cam_uvp_t_t, *crio_cal.n_cam_ocp_t_t, *crio_cal.f_cam_ocp_t_t,
               *crio_cal.n_cam_ovp_s_t, *crio_cal.f_cam_ovp_s_t, *crio_cal.n_cam_uvp_s_t,
               *crio_cal.f_cam_uvp_s_t, *crio_cal.n_cam_ocp_s_t, *crio_cal.f_cam_ocp_s_t]
    timings = [int(x) for x in timings]

    LOGGER.info(f"Start-up and trip timings: {timings}")

    crio.set_time(*timings)

    # 3. Configure the OCP for the N-CAM

    crio.set_n_cam_ocp(*crio_cal.n_cam_ocp)

    # 4. Check the OCP for the N-CAM

    ocp = crio.get_n_cam_ocp()

    LOGGER.info(f"N-CAM OCP: {ocp}")

    for index in range(NUM_POWERLINES):

        if ocp[index] != crio_cal.n_cam_ocp[index]:

            raise AEUError(f"N-CAM OCP for PSU{index + 1} is {ocp[index]} but should be {crio_cal.n_cam_ocp[index]}")

    # 5. Configure the OVP for the N-CAM

    crio.set_n_cam_ovp(*crio_cal.n_cam_ovp)

    # 6. Check the OVP for the N-CAM

    ovp = crio.get_n_cam_ovp()

    LOGGER.info(f"N-CAM OVP: {crio.get_n_cam_ovp()}")

    for index in range(NUM_POWERLINES):

        if ovp[index] != crio_cal.n_cam_ovp[index]:

            raise AEUError(f"N-CAM OVP for PSU{index + 1} is {ovp[index]} but should be {crio_cal.n_cam_ovp[index]}")

    # 7. Configure the UVP for the N-CAM

    crio.set_n_cam_uvp(*crio_cal.n_cam_uvp)

    # 8. Check the UVP for the N-CAM

    uvp = crio.get_n_cam_uvp()

    LOGGER.info(f"N-CAM UVP: {uvp}")

    for index in range(NUM_POWERLINES):
        if uvp[index] != crio_cal.n_cam_uvp[index]:
            raise AEUError(f"N-CAM UVP for PSU{index + 1} is {uvp[index]} but should be {crio_cal.n_cam_uvp[index]}")

    for psu_index in range(1, 7):

        psu: PSUInterface = setup.gse.aeu[f"psu{psu_index}"].device
        psu.reconnect()
        psu_cal = setup.gse.aeu[f"psu{psu_index}"].calibration
        voltage_name = VOLTAGES[psu_index - 1]

        # Configure the current

        psu.set_current(psu_cal.n_cam_current)

        # Check the current

        current_setpoint = psu.get_current_config()

        LOGGER.info(f"Current for {voltage_name} (PSU{psu_index}): {current_setpoint}")

        if current_setpoint != psu_cal.n_cam_current:

            raise AEUError(f"Current setpoint for PSU{psu_index} ({current_setpoint}) should be {psu_cal.n_cam_current}")

        # Configure the current protection

        psu.set_ocp(psu_cal.n_cam_ocp)

        # Check the current protection

        ocp = psu.get_ocp()

        LOGGER.info(f"OCP for {voltage_name} (PSU{psu_index}): {ocp}")

        if ocp != psu_cal.n_cam_ocp:

            raise AEUError(
                f"OCP for PSU{psu_index} ({ocp}) should be {psu_cal.n_cam_ocp}")

        # Configure the voltage

        psu.set_voltage(psu_cal.n_cam_voltage)

        # Check the voltage

        voltage_setpoint = psu.get_voltage_config()

        LOGGER.info(f"Voltage for {voltage_name} (PSU{psu_index}): {voltage_setpoint}")

        if voltage_setpoint != psu_cal.n_cam_voltage:

            raise AEUError(
                f"Voltage setpoint for PSU{psu_index} ({voltage_setpoint}) should be {psu_cal.n_cam_voltage}")

        # Configure the OVP

        psu.set_ovp(psu_cal.n_cam_ovp)

        # Check the OVP

        ovp = psu.get_ovp()

        LOGGER.info(f"OVP for {voltage_name} (PSU{psu_index}): {ovp}")

        if ovp != psu_cal.n_cam_ovp:

            raise AEUError(
                f"OVP for PSU{psu_index} ({ovp}) should be {psu_cal.n_cam_ovp}")

        # Configure the operation mode to be prioritised when the output is turned on

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)

        # Check the operation mode to be prioritised when the output is turned on

        priority_mode = psu.get_priority_mode()

        LOGGER.info(f"Prioritised operation mode for {voltage_name} (PSU{psu_index}): {priority_mode}")

        if priority_mode != PriorityMode.CONSTANT_CURRENT:

            raise AEUError(
                f"The priority mode for PSU{psu_index} ({priority_mode}) should be {PriorityMode.CONSTANT_CURRENT}")

        # Turn on the signal output

        psu.set_output_status(IntSwitch.ON)

        # Check the output status

        LOGGER.info(f"Output status for {voltage_name} (PSU{psu_index}): {psu.get_output_status()}")

        if psu.get_output_status() != IntSwitch.ON:

            raise AEUError(f"The output status for PSU{psu_index} should be ON")

    # 81. Turn on the secondary power lines in N-CAM

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)

    # 82. Check whether the secondary power lines are on

    LOGGER.info(f"Secondary power lines of N-CAM: {crio.get_n_cam_secondary_power_status()}")

    if crio.get_n_cam_secondary_power_status() != IntSwitch.ON:

        raise AEUError("The N-CAM secondary power lines should be ON")

    # 83. Get the secondary power line voltage quality for N-CAM

    voltage_quality = crio.get_n_cam_voltage_quality()

    LOGGER.info(f"Secondary power line voltage quality for N-CAM: {voltage_quality}")

    for index in range(NUM_POWERLINES):

        if voltage_quality[index] != 0:

            raise AEUError(f"Secondary power line voltage quality for N-CAM for {VOLTAGES[index]}: "
                           f"{voltage_quality[index]}({VOLTAGE_QUALITY[voltage_quality[index]]})")

    # 84. Get the secondary power line current quality for N-CAM

    current_quality = crio.get_n_cam_current_quality()

    LOGGER.info(f"Secondary power line current quality for N-CAM: {current_quality}")

    for index in range(NUM_POWERLINES):

        if current_quality[index] != 0:

            raise AEUError(f"Secondary power line current quality for N-CAM for {VOLTAGES[index]}: "
                           f"{current_quality[index]}({CURRENT_QUALITY[current_quality[index]]})")

    # 85. Measure the voltage values in N-CAM

    LOGGER.info(f"Measured voltages in N-CAM: {crio.get_n_cam_voltage()}")

    # 86. Measure the current values in N-CAM

    LOGGER.info(f"Measured currents in N-CAM: {crio.get_n_cam_current()}")


@building_block
def f_cam_swon():
    """ Power on F-CAM.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).
    """

    LOGGER.info("Switch on the F-CAM")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device

    crio_cal = setup.gse.aeu.crio.calibration

    reconnect(crio)

    # This command is only supposed to be executed when both the N- and the F-CAM were powered off

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]
    f_cam_powered = crio_data["F-CAM"]

    if n_cam_powered:

        raise AEUError("N-CAM already powered on")

    if f_cam_powered:

        raise AEUError("F-CAM already powered on")

    # 1. Change the operating mode to "Functional & TVAC Operating Mode"

    crio.set_operating_mode(OperatingMode.FC_TVAC)

    # 2. Check the actual operating mode

    operating_mode = crio.get_operating_mode()

    LOGGER.info(f"Operating mode: {operating_mode} ({OperatingMode(operating_mode).name})")

    if operating_mode != OperatingMode.FC_TVAC:

        raise AEUError(f"The current operating mode ({operating_mode}) should be FC_TVAC")

    # 3. Configure the OCP for the F-CAM

    crio.set_f_cam_ocp(*crio_cal.f_cam_ocp)

    # 4. Check the OCP for the F-CAM

    ocp = crio.get_f_cam_ocp()

    LOGGER.info(f"F-CAM OCP: {ocp}")

    for index in range(NUM_POWERLINES):

        if ocp[index] != crio_cal.f_cam_ocp[index]:

            raise AEUError(f"F-CAM OCP for PSU{index + 1} is {ocp[index]} but should be {crio_cal.f_cam_ocp[index]}")

    # 5. Configure the OVP for the F-CAM

    crio.set_f_cam_ovp(*crio_cal.f_cam_ovp)

    # 6. Check the OVP for the F-CAM

    ovp = crio.get_f_cam_ovp()

    LOGGER.info(f"F-CAM OVP: {ovp}")

    for index in range(NUM_POWERLINES):

        if ovp[index] != crio_cal.f_cam_ovp[index]:

            raise AEUError(f"F-CAM OVP for PSU{index + 1} is {ovp[index]} but should be {crio_cal.f_cam_ovp[index]}")

    # 7. Configure the UVP for the F-CAM

    crio.set_f_cam_uvp(*crio_cal.f_cam_uvp)

    # 8. Check the UVP for the F-CAM

    uvp = crio.get_f_cam_uvp()

    LOGGER.info(f"F-CAM UVP: {uvp}")

    for index in range(NUM_POWERLINES):

        if uvp[index] != crio_cal.f_cam_uvp[index]:

            raise AEUError(f"F-CAM UVP for PSU{index + 1} is {uvp[index]} but should be {crio_cal.f_cam_uvp[index]}")

    for psu_index in range(1, 7):

        psu: PSUInterface = setup.gse.aeu[f"psu{psu_index}"].device
        psu.reconnect()
        psu_cal = setup.gse.aeu[f"psu{psu_index}"].calibration
        voltage_name = VOLTAGES[psu_index - 1]

        # Configure the current

        psu.set_current(psu_cal.f_cam_current)

        # Check the current

        current_setpoint = psu.get_current_config()

        LOGGER.info(f"Current for {voltage_name} (PSU{psu_index}): {current_setpoint}")

        if current_setpoint != psu_cal.f_cam_current:

            raise AEUError(
                f"Current setpoint for PSU{psu_index} ({current_setpoint}) should be {psu_cal.f_cam_current}")

        # Configure the current protection

        psu.set_ocp(psu_cal.f_cam_ocp)

        # Check the current protection

        ocp = psu.get_ocp()

        LOGGER.info(f"OCP for {voltage_name} (PSU{psu_index}): {ocp}")

        if ocp != psu_cal.f_cam_ocp:

            raise AEUError(
                f"OCP for PSU{psu_index} ({ocp}) should be {psu_cal.f_cam_ocp}")


        # Configure the voltage

        psu.set_voltage(psu_cal.f_cam_voltage)

        # Check the voltage

        voltage_setpoint = psu.get_voltage_config()

        LOGGER.info(f"Voltage for {voltage_name} (PSU{psu_index}): {voltage_setpoint}")

        if voltage_setpoint != psu_cal.f_cam_voltage:

            raise AEUError(
                f"Voltage setpoint for PSU{psu_index} ({voltage_setpoint}) should be {psu_cal.f_cam_voltage}")

        # Configure the OVP

        psu.set_ovp(psu_cal.f_cam_ovp)

        # Check the OVP

        ovp = psu.get_ovp()

        LOGGER.info(f"OVP for {voltage_name} (PSU{psu_index}): {ovp}")

        if ovp != psu_cal.f_cam_ovp:

            raise AEUError(
                f"OVP for PSU{psu_index} ({ovp}) should be {psu_cal.f_cam_ovp}")

        # Configure the operation mode to be prioritised when the output is turned on

        psu.set_priority_mode(PriorityMode.CONSTANT_CURRENT)

        # Check the operation mode to be prioritised when the output is turned on

        priority_mode = psu.get_priority_mode()

        LOGGER.info(f"Prioritised operation mode for {voltage_name} (PSU{psu_index}): {priority_mode}")

        if priority_mode != PriorityMode.CONSTANT_CURRENT:

            raise AEUError(
                f"The priority mode for PSU{psu_index} ({priority_mode}) should be {PriorityMode.CONSTANT_CURRENT}")

        # Turn on the signal output

        psu.set_output_status(IntSwitch.ON)

        # Check the output status

        LOGGER.info(f"Output status for {voltage_name} (PSU{psu_index}): {psu.get_output_status()}")

        if psu.get_output_status() != IntSwitch.ON:

            raise AEUError(f"The output status for PSU{psu_index} should be ON")

    # 81. Turn on the secondary power lines in F-CAM

    crio.set_f_cam_secondary_power_status(IntSwitch.ON)

    # 82. Check whether the secondary power lines are on

    LOGGER.info(f"Secondary power lines of F-CAM: {crio.get_f_cam_secondary_power_status()}")

    if crio.get_f_cam_secondary_power_status() != IntSwitch.ON:

        raise AEUError("The F-CAM secondary power lines should be ON")

    # 83. Get the secondary power line voltage quality for F-CAM

    voltage_quality = crio.get_f_cam_voltage_quality()

    LOGGER.info(f"Secondary power line voltage quality for N-CAM: {voltage_quality}")

    for index in range(NUM_POWERLINES):

        if voltage_quality[index] != 0:

            raise AEUError(f"Secondary power line voltage quality for F-CAM for {VOLTAGES[index]}: "
                           f"{voltage_quality[index]}({VOLTAGE_QUALITY[voltage_quality[index]]})")

    # 84. Get the secondary power line current quality for F-CAM

    current_quality = crio.get_f_cam_current_quality()

    LOGGER.info(f"Secondary power line current quality for F-CAM: {current_quality}")

    for index in range(NUM_POWERLINES):

        if current_quality[index] != 0:

            raise AEUError(f"Secondary power line current quality for F-CAM for {VOLTAGES[index]}: "
                           f"{current_quality[index]}({CURRENT_QUALITY[current_quality[index]]})")



    # 85. Measure the voltage values in F-CAM

    LOGGER.info(f"Measured voltages in F-CAM: {crio.get_f_cam_voltage()}")

    # 86. Measure the current values in F-CAM

    LOGGER.info(f"Measured currents in F-CAM: {crio.get_f_cam_current()}")


#######################
# Switch off the camera
#######################


@building_block
def n_cam_swoff():
    """ Power off N-CAM.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).
    """

    LOGGER.info("Switch off the N-CAM")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    reconnect(crio)

    # This command is only supposed to be executed when:
    #   - the N-CAM was powered on;
    #   - the N-CAM clocks were not enabled.

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]
    f_cam_powered = crio_data["F-CAM"]

    if not n_cam_powered:

        if f_cam_powered:
            raise AEUError("F-CAM was powered on, not the N-CAM")

        raise AEUError("N-CAM already powered off")

    # 1-12. Confirm the actual N-CAM status

    confirm_n_cam_status()

    # 13. Turn off the secondary power lines in N-CAM

    crio.set_n_cam_secondary_power_status(IntSwitch.OFF)

    # 14. Check whether the secondary power lines are off

    LOGGER.info(f"Secondary power lines of N-CAM: {crio.get_n_cam_secondary_power_status()}")

    if crio.get_n_cam_secondary_power_status() != IntSwitch.OFF:

        raise AEUError("The N-CAM secondary power status should be OFF")

    # 15. Measure the voltage values in N-CAM

    LOGGER.info(f"Measured voltages in N-CAM: {crio.get_n_cam_voltage()}")

    # 16. Measure the current values in N-CAM

    LOGGER.info(f"Measured currents in N-CAM: {crio.get_n_cam_current()}")

    for psu_index in range(1, 7):

        psu: PSUInterface = setup.gse.aeu[f"psu{psu_index}"].device
        psu.reconnect()
        voltage_name = VOLTAGES[psu_index - 1]

        # Turn off the signal output

        psu.set_output_status(IntSwitch.OFF)

        # Check the output status of V_CCD (PSU1)

        LOGGER.info(f"Output status for {voltage_name} (PSU{psu_index}): {psu.get_output_status()}")

        if psu.get_output_status() != IntSwitch.OFF:

            raise AEUError(f"The output status for PSU{psu_index} should be OFF")

    crio.set_operating_mode(OperatingMode.STANDBY)

    operating_mode = crio.get_operating_mode()

    LOGGER.info(f"Operating mode: {operating_mode} ({OperatingMode(operating_mode).name})")

    if operating_mode != OperatingMode.STANDBY:

        raise AEUError(f"The current operating mode ({operating_mode}) should be STANDBY")


@building_block
def f_cam_swoff():
    """ Power off F-CAM.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).
    """

    LOGGER.info("Switch off the F-CAM")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    reconnect(crio)

    # This command is only supposed to be executed when:
    #   - the F-CAM was powered on;
    #   - the F-CAM clocks were not enabled

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]
    f_cam_powered = crio_data["F-CAM"]

    if not f_cam_powered:

        if n_cam_powered:
            raise AEUError("N-CAM was powered on, not the F-CAM")

        raise AEUError("F-CAM already powered off")

    # 1-12. Confirm the actual F-CAM status

    confirm_f_cam_status()

    # 13. Turn off the secondary power lines in F-CAM

    crio.set_f_cam_secondary_power_status(IntSwitch.OFF)

    # 14. Check whether the secondary power lines are off

    if crio.get_f_cam_secondary_power_status() != IntSwitch.OFF:

        raise AEUError("The F-CAM secondary power status should be OFF")

    # 15. Measure the voltage values in F-CAM

    LOGGER.info(f"Measured voltages in F-CAM: {crio.get_f_cam_voltage()}")

    # 16. Measure the current values in F-CAM

    LOGGER.info(f"Measured currents in F-CAM: {crio.get_f_cam_current()}")

    for psu_index in range(1, 7):

        psu: PSUInterface = setup.gse.aeu[f"psu{psu_index}"].device
        psu.reconnect()
        voltage_name = VOLTAGES[psu_index - 1]

        # Turn off the signal output

        psu.set_output_status(IntSwitch.OFF)

        # Check the output status of V_CCD (PSU1)

        LOGGER.info(f"Output status for {voltage_name} (PSU{psu_index}): {psu.get_output_status()}")

        if psu.get_output_status() != IntSwitch.OFF:

            raise AEUError(f"The output status for PSU{psu_index} should be OFF")

    crio.set_operating_mode(OperatingMode.STANDBY)

    operating_mode = crio.get_operating_mode()

    LOGGER.info(f"Operating mode: {operating_mode} ({OperatingMode(operating_mode).name})")

    if operating_mode != OperatingMode.STANDBY:

        raise AEUError(f"The current operating mode ({operating_mode}) should be STANDBY")


###################
# Enable the clocks
###################


def get_n_cam_image_cycle_time_id(image_cycle_time: float):
    """ Returns the SyncData for the given image cycle time for the N-CAM.

    Args:
        - image_cycle_time: Image cycle time for the N-CAM [s].  Allowed values are: 25, 31.25, 37.5, 43.75, and 50s.

    Returns: SyncData object for the given image cycle time for the N-CAM
    """

    if image_cycle_time < 25:

        raise AEUError("The minimum image cycle time to configure for the N-CAM is 25s")

    if image_cycle_time > 50:

        raise AEUError("The maximum image cycle time to configure for the N-CAM is 50s")

    if image_cycle_time % 6.25 != 0:

        raise AEUError("Only the following values are allow for the image cycle time for the N-CAM: 25, 31.25, 37.5, "
                       "43.75, and 50s")

    awg2_cal = GlobalState.setup.gse.aeu.awg2.calibration

    offset_index = int((image_cycle_time - 25) // 6.25)
    identifier = string.ascii_uppercase[offset_index]

    sync_data_string = awg2_cal.n_cam_sync_data[identifier]

    return SyncData(sync_data_string)


@building_block
def n_cam_sync_enable(image_cycle_time=25, svm_nom=IntSwitch.ON, svm_red=IntSwitch.ON):
    """ Switch on N-CAM clocks.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).

        - AWG1, channel 1: Clk_50MHz
        - AWG2:
            - channel 1: Clk_ccdread (25s)
            - channel 2: SVM

    Args:
        - image_cycle_time: Image cycle time [s].
        - svm_nom: Whether or not the nominal SVM clocks (Clk_heater and Clk_50Hz) should be enabled.
        - svm_red: Whether or not the redundant SVM clocks (Clk_heater and Clk_50MHz) should be enabled.
    """

    LOGGER.info(f"Enable the N-CAM sync pulses (for an image cycle time of {image_cycle_time}s)")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    awg1: AWGInterface = setup.gse.aeu.awg1.device
    awg2: AWGInterface = setup.gse.aeu.awg2.device

    awg1_cal = setup.gse.aeu.awg1.calibration
    awg2_cal = setup.gse.aeu.awg2.calibration
    awg2_sync_data = get_n_cam_image_cycle_time_id(image_cycle_time)

    reconnect(crio, awg1, awg2)

    # This command is only supposed to be executed when the N-CAM was powered on
    # (there is no need to make sure the sync signals were disabled first)

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]

    if not n_cam_powered:

        raise AEUError("Power on N-CAM before enabling the N-CAM sync signals")

    # 1-12. Confirm the actual N-CAM status

    confirm_n_cam_status()

    # 13. Configure the AWG1 channel (Clk_50MHz)

    awg1.set_channel(1)

    # 14. Check the channel for AWG1

    LOGGER.info(f"Channel selected for AWG1: {awg1.get_channel()}")

    # 15. Configure the waveform type

    awg1.set_waveform_type(Waveform.SQUARE)

    # 16. Configure the output load

    awg1.set_output_load(awg1_cal.output_load)

    # 17. Configure the amplitude

    awg1.set_amplitude(awg1_cal.amplitude)

    # 18. Configure the DC offset

    awg1.set_dc_offset(awg1_cal.dc_offset)

    # 19. Configure the duty cycle

    awg1.set_duty_cycle(awg1_cal.duty_cycle)

    # 20. Configure the frequency

    awg1.set_frequency(awg1_cal.frequency)

    # 21. Turn on the channel

    awg1.set_output_status(Switch.ON)

    # 22. Check that there are no execution errors

    LOGGER.info(f"Execution error register: {awg1.execution_error_register()}")

    # 23. Check that there are no query errors

    LOGGER.info(f"Query error register: {awg1.query_error_register()}")

    # 24. Configure the AWG2 channel (Clk_ccdread)

    awg2.set_channel(1)

    # 25. Check the channel for AWG2

    LOGGER.info(f"Channel selected for AWG2: {awg2.get_channel()}")

    # 26. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 27. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 28. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 29. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 30. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 31. Define ARB1

    awg2.define_arb_waveform(ARB.ARB1, f"CCDREAD{awg2_sync_data.id}", Switch.OFF)
    LOGGER.info(f"Definition of ARB1: {awg2.get_arb1_def()}")

    # 32. Load ARB1 #46000 [See AD5; Annex 5.1]

    arb_filename = awg2_sync_data.ccdread_arb_data
    arb_data = ArbData()
    arb_data.init_from_file(arb_filename)
    LOGGER.info(f"Loading ARB data from {arb_filename}")

    arb_data.string
    awg2.load_arb1_ascii(arb_data.string)
    # awg2.load_arb1_data(awg2_sync_data.ccdread_arb_data)
    time.sleep(2)

    # 33. Check waveform configuration of ARB1

    LOGGER.info(f"Waveform configuration of ARB1: {awg2.get_arb1()}")

    # 34. Check the definition of ARB1

    LOGGER.info(f"Definition of ARB1: {awg2.get_arb1_def()}")

    # 35. Set the output waveform with ARB1 data

    awg2.set_arb_waveform(ARB.ARB1)

    # 36. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 37. Configure the AWG2 channel (Clk_heater)

    awg2.set_channel(2)

    # 38. Check the channel for AWG2

    LOGGER.info(f"Channel selected for AWG2: {awg2.get_channel()}")

    # 39. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 40. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 41. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 42. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 43. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 44. Define ARB2

    awg2.define_arb_waveform(ARB.ARB2, f"HEATER{awg2_sync_data.id}", Switch.OFF)

    # 45. Load ARB2 #46000 [See AD5; Annex 5.7]

    awg2.load_arb2_data(awg2_sync_data.heater_arb_data)
    time.sleep(2)

    # 46. Check waveform configuration of ARB2

    LOGGER.info(f"Waveform configuration of ARB2: {awg2.get_arb2()}")

    # 47. Check the definition of ARB2

    LOGGER.info(f"Definition of ARB2: {awg2.get_arb2_def()}")

    # 48. Set the output waveform with ARB2 data

    awg2.set_arb_waveform(ARB.ARB2)

    # 49. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 50. Synchronise both channels

    awg2.align()

    # 51. Check that there are no execution errors

    LOGGER.info(f"Execution error register: {awg2.execution_error_register()}")

    # 52. Check that there are no query errors

    LOGGER.info(f"Query error register: {awg2.query_error_register()}")

    # 53. Enable all clocks in N-CAM

    crio.set_n_cam_clock_status(IntSwitch.ON, IntSwitch.ON)

    # 54. Check that all clocks are enabled

    LOGGER.info(f"Output status for N-CAM clocks: {crio.get_n_cam_clock_status()}")

    # 55. Enable all SVM nominal clocks

    crio.set_svm_clock_status(svm_nom, svm_red, svm_nom, svm_red)

    # 56. Check that all nominal SVM clock are enabled

    LOGGER.info(f"Output status for SVM clocks: {crio.get_svm_clock_status()}")

    # aeu_metrics.GAEU_EXT_CYCLE_TIME.set(image_cycle_time)


@building_block
def f_cam_sync_enable(cam_nom=IntSwitch.ON, cam_red=IntSwitch.OFF, svm_nom=IntSwitch.ON,
                      svm_red=IntSwitch.ON):
    """ Switch on F-CAM clocks.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).

        - AWG1, channel 1: Clk_50MHz
        - AWG2:
            - channel 1: Clk_ccdread (25s)
            - channel 2: SVM

    Args:
        - cam_nom: Whether or not the nominal F-CAM clocks (Clk_ccdread and Clk_50MHz) should be enabled.
        - cam_red: Whether or not the redundant F-CAM clocks (Clk_ccdread and Clk_50MHz) should be enabled.
        - svm_nom: Whether or not the nominal SVM clocks (Clk_heater and Clk_50Hz) should be enabled.
        - svm_red: Whether or not the redundant SVM clocks (Clk_heater and Clk_50MHz) should be enabled.
    """

    LOGGER.info("Enable the F-CAM sync pulses")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    awg1: AWGInterface = setup.gse.aeu.awg1.device
    awg2: AWGInterface = setup.gse.aeu.awg2.device

    awg1_cal = setup.gse.aeu.awg1.calibration
    awg2_cal = setup.gse.aeu.awg2.calibration
    awg2_sync_data = SyncData(awg2_cal.f_cam_sync_data.F)

    reconnect(crio, awg1, awg2)

    # This command is only supposed to be executed when the F-CAM was powered on
    # (there is no need to make sure the sync signals were disabled first)

    crio_data = crio.get_led_status()
    f_cam_powered = crio_data["F-CAM"]

    if not f_cam_powered:

        raise AEUError("Power on F-CAM before enabling the F-CAM sync signals")

    # 1-12. Confirm the actual F-CAM status

    confirm_f_cam_status()

    # 13. Configure the AWG1 channel (Clk_50MHz)

    awg1.set_channel(1)

    # 14. Check the channel for AWG1

    LOGGER.info(f"Channel selected for AWG1: {awg1.get_channel()}")

    # 15. Configure the waveform type

    awg1.set_waveform_type(Waveform.SQUARE)

    # 16. Configure the output load

    awg1.set_output_load(awg1_cal.output_load)

    # 17. Configure the amplitude

    awg1.set_amplitude(awg1_cal.amplitude)

    # 18. Configure the DC offset

    awg1.set_dc_offset(awg1_cal.dc_offset)

    # 19. Configure the duty cycle

    awg1.set_duty_cycle(awg1_cal.duty_cycle)

    # 20. Configure the frequency

    awg1.set_frequency(awg1_cal.frequency)

    # 21. Turn on the channel

    awg1.set_output_status(Switch.ON)

    # 22. Check that there are no execution errors

    LOGGER.info(f"Execution error register: {awg1.execution_error_register()}")

    # 23. Check that there are no query errors

    LOGGER.info(f"Query error register: {awg1.query_error_register()}")

    # 24. Configure the AWG2 channel (Clk_ccdread)

    awg2.set_channel(1)

    # 25. Check the channel for AWG2

    LOGGER.info(f"Channel selected for AWG2: {awg2.get_channel()}")

    # 26. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 27. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 28. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 29. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 30. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 31. Define ARB1

    awg2.define_arb_waveform(ARB.ARB1, f"FCCDREAD", Switch.OFF)

    # 32. Load ARB1 #46000 [See AD5; Annex 5.6]

    awg2.load_arb1_data(awg2_sync_data.ccdread_arb_data)
    time.sleep(2)

    # 33. Check waveform configuration of ARB1

    LOGGER.info(f"Waveform configuration of ARB1: {awg2.get_arb1()}")

    # 34. Check the definition of ARB1

    LOGGER.info(f"Definition of ARB1: {awg2.get_arb1_def()}")

    # 35. Set the output waveform with ARB1 data

    awg2.set_arb_waveform(ARB.ARB1)

    # 36. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 37. Configure the AWG2 channel (Clk_heater)

    awg2.set_channel(2)

    # 38. Check the channel for AWG2

    LOGGER.info(f"Channel selected for AWG2: {awg2.get_channel()}")

    # 39. Configure the waveform type

    awg2.set_waveform_type(Waveform.ARB)

    # 40. Configure the output load

    awg2.set_output_load(awg2_cal.output_load)

    # 41. Configure the amplitude

    awg2.set_amplitude(awg2_cal.amplitude)

    # 42. Configure the DC offset

    awg2.set_dc_offset(awg2_cal.dc_offset)

    # 43. Configure the frequency

    awg2.set_frequency(awg2_sync_data.frequency)

    # 44. Define ARB2

    awg2.define_arb_waveform(ARB.ARB2, f"HEATER", Switch.OFF)

    # 45. Load ARB2 #46000 [See AD5; Annex 5.12]

    awg2.load_arb2_data(awg2_sync_data.heater_arb_data)
    time.sleep(2)

    # 46. Check waveform configuration of ARB2

    LOGGER.info(f"Waveform configuration of ARB2: {awg2.get_arb2()}")

    # 47. Check the definition of ARB2

    LOGGER.info(f"Definition of ARB2: {awg2.get_arb2_def()}")

    # 48. Set the output waveform with ARB2 data

    awg2.set_arb_waveform(ARB.ARB2)

    # 49. Turn on the channel

    awg2.set_output_status(Switch.ON)

    # 50. Synchronise both channels

    awg2.align()

    # 51. Check that there are no execution errors

    LOGGER.info(f"Execution error register: {awg2.execution_error_register()}")

    # 52. Check that there are no query errors

    LOGGER.info(f"Query error register: {awg2.query_error_register()}")

    # 53. Enable all clocks in F-CAM

    crio.set_f_cam_clock_status(cam_nom, cam_red, cam_nom, cam_red)

    # 54. Check that all clocks are enabled

    LOGGER.info(f"Output status for F-CAM clocks: {crio.get_f_cam_clock_status()}")

    # 55. Enable all SVM nominal clocks

    crio.set_svm_clock_status(svm_nom, svm_red, svm_nom, svm_red)

    # 56. Check that all nominal SVM clock are enabled

    LOGGER.info(f"Output status for SVM clocks: {crio.get_svm_clock_status()}")

    aeu_metrics.GAEU_EXT_CYCLE_TIME.set(2.5)


def get_n_cam_cycle_time():
    """ Return the N-CAM cycle time.

    Returns: N-CAM cycle time [s].
    """

    setup = GlobalState.setup

    awg2: AWGInterface = setup.gse.aeu.awg2.device

    identifier = awg2.get_arb1_def()[0][-1]

    awg2_cal = setup.gse.aeu.awg2.calibration
    sync_data_string = awg2_cal.n_cam_sync_data[identifier]

    return float(SyncData(sync_data_string).image_cycle_time)


def get_f_cam_cycle_time():
    """ Return the F-CAM cycle time.

    Returns: F-CAM cycle time [s].
    """

    awg2_cal = GlobalState.setup.gse.aeu.awg2.calibration
    sync_data_string = awg2_cal.f_cam_sync_data["F"]

    return float(SyncData(sync_data_string).image_cycle_time)

####################
# Disable the clocks
####################


@building_block
def n_cam_sync_disable():
    """ Switch off N-CAM clocks.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).

        - AWG1, channel 1: Clk_50MHz
        - AWG2:
            - channel 1: Clk_ccdread (25s)
            - channel 2: SVM
    """

    LOGGER.info("Disable the N-CAM sync pulses")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    awg1: AWGInterface = setup.gse.aeu.awg1.device
    awg2: AWGInterface = setup.gse.aeu.awg2.device

    reconnect(crio, awg1, awg2)

    crio_data = crio.get_led_status()
    n_cam_powered = crio_data["N-CAM"]

    # This command is only supposed to be executed when the N-CAM sync signals were enabled

    if not n_cam_powered and not (crio_data["Clk_50MHz"] or crio_data["Clk_ccdread"] or crio_data["Clk_heater"]):

        raise AEUError("No sync signals enabled for the N-CAM")

    # 1-12. Confirm the actual N-CAM status

    confirm_n_cam_status()

    # 13. Disable all clocks in N-CAM

    crio.set_n_cam_clock_status(IntSwitch.OFF, IntSwitch.OFF)

    # 14. Check that all clocks are disabled

    LOGGER.info(f"Output status for N-CAM clocks: {crio.get_n_cam_clock_status()}")

    for index in range(NUM_CLK_N_CAM):

        if crio.get_n_cam_clock_status()[index] != 0:

            raise AEUError(f"The output status of the N-CAM {N_CAM_CLK[index]} should be OFF")

    # 15. Disable all SVM nominal clocks

    crio.set_svm_clock_status(IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF)

    # 16. Check that all nominal SVM clock are disabled

    LOGGER.info(f"Output status for SVM clocks: {crio.get_svm_clock_status()}")

    for index in range(NUM_CLK_TCS):

        if crio.get_svm_clock_status()[index] != 0:

            raise AEUError(f"The output status of the TCS {TCS_CLK[index]} should be OFF")

    # 17. Configure the channel for AWG2 (Clk_heater)

    awg2.set_channel(2)

    # 18. Turn off the channel

    awg2.set_output_status(Switch.OFF)

    # 19. Configure the channel for AWG2 (Clk_ccdread)

    awg2.set_channel(1)

    # 20. Turn off the channel

    awg2.set_output_status(Switch.OFF)

    # 21. Configure the channel for AWG1 (Clk_50MHz)

    awg1.set_channel(1)

    # 22. Turn off the channel

    awg1.set_output_status(Switch.OFF)


@building_block
def f_cam_sync_disable():
    """ Switch off F-CAM clocks.

    Procedure taken from Sect. 4 (Use cases overview) in PTO-EVO-SYS-MA-0261 (PLATO-AEU CAM TEST EGSE User Manual).

        - AWG1, channel 1: Clk_50MHz
        - AWG2:
            - channel 1: Clk_Fccdread
            - channel 2: SVM
    """

    LOGGER.info("Disable the F-CAM sync pulses")

    setup = GlobalState.setup

    crio: CRIOInterface = setup.gse.aeu.crio.device
    awg1: AWGInterface = setup.gse.aeu.awg1.device
    awg2: AWGInterface = setup.gse.aeu.awg2.device

    reconnect(crio, awg1, awg2)

    # This command is only supposed to be executed when the F-CAM sync signals were enabled

    crio_data = crio.get_led_status()
    f_cam_powered = crio_data["F-CAM"]

    if not f_cam_powered and not (crio_data["Clk_50MHz"] or crio_data["Clk_ccdread"] or crio_data["Clk_heater"]
                                  or crio_data["Clk_F_FEE_N"] or crio_data["Clk_F_FEE_R"]):

        raise AEUError("No sync signals enabled for the F-CAM")

    # 1-12. Confirm the actual F-CAM status

    confirm_f_cam_status()

    # 13. Disable all clocks in F-CAM

    crio.set_f_cam_clock_status(IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF)

    # 14. Check that all clocks are disabled

    LOGGER.info(f"Output status for F-CAM clocks: {crio.get_f_cam_clock_status()}")

    for index in range(NUM_CLK_F_CAM):

        if crio.get_f_cam_clock_status()[index] != 0:

            raise AEUError(f"The output status of the F-CAM {F_CAM_CLK[index]} should be OFF")

    # 15. Disable all SVM nominal clocks

    crio.set_svm_clock_status(IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF, IntSwitch.OFF)

    # 16. Check that all nominal SVM clock are disabled

    LOGGER.info(f"Output status for SVM clocks: {crio.get_svm_clock_status()}")

    for index in range(NUM_CLK_TCS):

        if crio.get_svm_clock_status()[index] != 0:

            raise AEUError(f"The output status of the TCS {TCS_CLK[index]} should be OFF")

    # 17. Configure the channel for AWG2 (Clk_heater)

    awg2.set_channel(2)

    # 18. Turn off the channel

    awg2.set_output_status(Switch.OFF)

    # 19. Configure the channel for AWG2 (Clk_Fccdread)

    awg2.set_channel(1)

    # 20. Turn off the channel

    awg2.set_output_status(Switch.OFF)

    # 21. Configure the channel for AWG1 (Clk_50MHz)

    awg1.set_channel(1)

    # 22. Turn off the channel

    awg1.set_output_status(Switch.OFF)


#####################
# Additional commands
#####################


@building_block
def set_operating_mode(operating_mode: OperatingMode):
    """ Change the operating mode.

    Possible values are:

        - OperatingMode.STANDBY: stand-by mode;
        - OperatingMode.SELFTEST: self-test mode;
        - OperatingMode.ALIGNMENT: alignment operating mode;
        - OperatingMode.FC_TVAC: functional-check and TVAC mode.

    Args:
        - operating_mode: Operating mode to change to.
    """

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    crio.set_operating_mode(operating_mode)


def get_operating_mode() -> OperatingMode:
    """ Return the actual operating mode.

    To understand the meaning of the returned value,check:

        egse.aeu.aeu.OPERATING_MODE[returned_value]

    Returns: Actual operating mode.
    """

    crio: CRIOInterface = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_operating_mode()


def get_psu_voltage_setpoints():
    """ Returns the PSU voltage setpoints [V].

    Returns:
        - Voltage setpoint for V_CCD [V], from PSU1.
        - Voltage setpoint for V_CLK [V], from PSU2.
        - Voltage setpoint for V_AN1 [V], from PSU3.
        - Voltage setpoint for V_AN2 [V], from PSU4.
        - Voltage setpoint for V_AN3 [V], from PSU5.
        - Voltage setpoint for V_DIG [V], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_voltage_config()
    v_clk = psu2.get_voltage_config()
    v_an1 = psu3.get_voltage_config()
    v_an2 = psu4.get_voltage_config()
    v_an3 = psu5.get_voltage_config()
    v_dig = psu6.get_voltage_config()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_psu_voltages():
    """ Returns the PSU measured voltages [V].

    Returns:
        - Measured voltage for V_CCD [V], from PSU1.
        - Measured voltage for V_CLK [V], from PSU2.
        - Measured voltage for V_AN1 [V], from PSU3.
        - Measured voltage for V_AN2 [V], from PSU4.
        - Measured voltage for V_AN3 [V], from PSU5.
        - Measured voltage for V_DIG [V], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_voltage()
    v_clk = psu2.get_voltage()
    v_an1 = psu3.get_voltage()
    v_an2 = psu4.get_voltage()
    v_an3 = psu5.get_voltage()
    v_dig = psu6.get_voltage()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_psu_ovp():
    """ Returns the PSU Over-Protection Voltage (OVP) values [V].

    Returns:
        - Over-Protection Voltage (OVP) for V_CCD [V], from PSU1.
        - Over-Protection Voltage (OVP) for V_CLK [V], from PSU2.
        - Over-Protection Voltage (OVP) for V_AN1 [V], from PSU3.
        - Over-Protection Voltage (OVP) for V_AN2 [V], from PSU4.
        - Over-Protection Voltage (OVP) for V_AN3 [V], from PSU5.
        - Over-Protection Voltage (OVP) for V_DIG [V], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_ovp()
    v_clk = psu2.get_ovp()
    v_an1 = psu3.get_ovp()
    v_an2 = psu4.get_ovp()
    v_an3 = psu5.get_ovp()
    v_dig = psu6.get_ovp()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_psu_current_setpoints():
    """ Returns the PSU current setpoints [A].

    Returns:
        - Current setpoint for V_CCD [A], from PSU1.
        - Current setpoint for V_CLK [A], from PSU2.
        - Current setpoint for V_AN1 [A], from PSU3.
        - Current setpoint for V_AN2 [A], from PSU4.
        - Current setpoint for V_AN3 [A], from PSU5.
        - Current setpoint for V_DIG [A], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_current_config()
    v_clk = psu2.get_current_config()
    v_an1 = psu3.get_current_config()
    v_an2 = psu4.get_current_config()
    v_an3 = psu5.get_current_config()
    v_dig = psu6.get_current_config()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_psu_currents():
    """ Returns the PSU measured currents [A].

    Returns:
        - Measured current for V_CCD [A], from PSU1.
        - Measured current for V_CLK [A], from PSU2.
        - Measured current for V_AN1 [A], from PSU3.
        - Measured current for V_AN2 [A], from PSU4.
        - Measured current for V_AN3 [A], from PSU5.
        - Measured current for V_DIG [A], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_current()
    v_clk = psu2.get_current()
    v_an1 = psu3.get_current()
    v_an2 = psu4.get_current()
    v_an3 = psu5.get_current()
    v_dig = psu6.get_current()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_psu_ocp():
    """ Returns the PSU Over-Protection Current (OCP) values [A].

    Returns:
        - Over-Protection Current (OCP) for V_CCD [A], from PSU1.
        - Over-Protection Current (OCP) for V_CLK [A], from PSU2.
        - Over-Protection Current (OCP) for V_AN1 [A], from PSU3.
        - Over-Protection Current (OCP) for V_AN2 [A], from PSU4.
        - Over-Protection Current (OCP) for V_AN3 [A], from PSU5.
        - Over-Protection Current (OCP) for V_DIG [A], from PSU6.
    """

    setup = GlobalState.setup

    psu1: PSUInterface = setup.gse.aeu.psu1.device
    psu2: PSUInterface = setup.gse.aeu.psu2.device
    psu3: PSUInterface = setup.gse.aeu.psu3.device
    psu4: PSUInterface = setup.gse.aeu.psu4.device
    psu5: PSUInterface = setup.gse.aeu.psu5.device
    psu6: PSUInterface = setup.gse.aeu.psu6.device

    reconnect(psu1, psu2, psu3, psu4, psu5, psu6)

    v_ccd = psu1.get_ocp()
    v_clk = psu2.get_ocp()
    v_an1 = psu3.get_ocp()
    v_an2 = psu4.get_ocp()
    v_an3 = psu5.get_ocp()
    v_dig = psu6.get_ocp()

    return v_ccd, v_clk, v_an1, v_an2, v_an3, v_dig


def get_n_cam_voltages():
    """ Return the measured voltages for the N-CAM [V].

    Returns:
        - Measured N-CAM voltage for V_CCD [V].
        - Measured N-CAM voltage for V_CLK [V].
        - Measured N-CAM voltage for V_AN1 [V].
        - Measured N-CAM voltage for V_AN2 [V].
        - Measured N-CAM voltage for V_AN3 [V].
        - Measured N-CAM voltage for V_DIG [V].
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_voltage()


def get_f_cam_voltages():
    """ Return the measured voltages for the F-CAM [V].

    Returns:
        - Measured F-CAM voltage for V_CCD [V].
        - Measured F-CAM voltage for V_CLK [V].
        - Measured F-CAM voltage for V_AN1 [V].
        - Measured F-CAM voltage for V_AN2 [V].
        - Measured F-CAM voltage for V_AN3 [V].
        - Measured F-CAM voltage for V_DIG [V].
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_voltage()


def get_n_cam_uvp():
    """ Return the Under-Voltage Protection value (UVP) [V] for the N-CAM.

    Returns:
        - Under-Voltage Protection (UVP) for V_CCD [V], for the N-CAM.
        - Under-Voltage Protection (UVP) for V_CLK [V], for the N-CAM.
        - Under-Voltage Protection (UVP) for V_AN1 [V], for the N-CAM.
        - Under-Voltage Protection (UVP) for V_AN2 [V], for the N-CAM.
        - Under-Voltage Protection (UVP) for V_AN3 [V], for the N-CAM.
        - Under-Voltage Protection (UVP) for V_DIG [V], for the N-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_uvp()


def get_f_cam_uvp():
    """ Return the Under-Voltage Protection value (UVP) [V] for the F-CAM.

    Returns:
        - Under-Voltage Protection (UVP) for V_CCD [V], for the F-CAM.
        - Under-Voltage Protection (UVP) for V_CLK [V], for the F-CAM.
        - Under-Voltage Protection (UVP) for V_AN1 [V], for the F-CAM.
        - Under-Voltage Protection (UVP) for V_AN2 [V], for the F-CAM.
        - Under-Voltage Protection (UVP) for V_AN3 [V], for the F-CAM.
        - Under-Voltage Protection (UVP) for V_DIG [V], for the F-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_uvp()


def get_n_cam_ovp():
    """ Return the Over-Voltage Protection value (OVP) [V] for the N-CAM.

    Returns:
        - Over-Voltage Protection (OVP) for V_CCD [V], for the N-CAM.
        - Over-Voltage Protection (OVP) for V_CLK [V], for the N-CAM.
        - Over-Voltage Protection (OVP) for V_AN1 [V], for the N-CAM.
        - Over-Voltage Protection (OVP) for V_AN2 [V], for the N-CAM.
        - Over-Voltage Protection (OVP) for V_AN3 [V], for the N-CAM.
        - Over-Voltage Protection (OVP) for V_DIG [V], for the N-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_ovp()


def get_f_cam_ovp():
    """ Return the Over-Voltage Protection value (OVP) [V] for the F-CAM.

    Returns:
        - Over-Voltage Protection (OVP) for V_CCD [V], for the F-CAM.
        - Over-Voltage Protection (OVP) for V_CLK [V], for the F-CAM.
        - Over-Voltage Protection (OVP) for V_AN1 [V], for the F-CAM.
        - Over-Voltage Protection (OVP) for V_AN2 [V], for the F-CAM.
        - Over-Voltage Protection (OVP) for V_AN3 [V], for the F-CAM.
        - Over-Voltage Protection (OVP) for V_DIG [V], for the F-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_ovp()


def get_cam_currents():
    """ Return the measured currents for the N-CAM [A].

    Returns:
        - Measured N-CAM current for V_CCD [A].
        - Measured N-CAM current for V_CLK [A].
        - Measured N-CAM current for V_AN1 [A].
        - Measured N-CAM current for V_AN2 [A].
        - Measured N-CAM current for V_AN3 [A].
        - Measured N-CAM current for V_AN3 [A].
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_current()


def get_f_cam_currents():
    """ Return the measured currents for the F-CAM [A].

    Returns:
        - Measured F-CAM current for V_CCD [A].
        - Measured F-CAM current for V_CLK [A].
        - Measured F-CAM current for V_AN1 [A].
        - Measured F-CAM current for V_AN2 [A].
        - Measured F-CAM current for V_AN3 [A].
        - Measured F-CAM current for V_AN3 [A].
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_current()


def get_n_cam_ocp():
    """ Return the Over-Current Protection value (OCP) [A] for the N-CAM.

    Returns:
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the N-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_ocp()


def get_f_cam_ocp():
    """ Return the Over-Current Protection value (OCP) [A] for the F-CAM.

    Returns:
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
        - Over-Current Protection (OVP) for OCP [A], for the F-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_ocp()


def get_n_cam_sync_status() -> (IntSwitch, IntSwitch):
    """ Return whether or not the clocks are enabled or not for the N-CAM.

    For the N-CAM, the clocks are Clk_50MHz and Clk_ccdread.

    Returns:
        - Boolean indicating whether or not the Clk_50MHz has been enabled for the N-CAM.
        - Boolean indicating whether or not eh Clk_ccdread has been enabled for the N-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_clock_status()


def get_f_cam_sync_status() -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
    """ Return whether or not the clocks are enabled or not for the F-CAM.

    For the F-CAM, the clocks are Clk_50MHz and Clk_ccdread, both nominal and redundant.

    Returns:
        - Boolean indicating whether or not the Clk-50MHz_nom has been enabled for the F-CAM.
        - Boolean indicating whether or not the Clk-50MHz_red has been enabled for the F-CAM.
        - Boolean indicating whether or not the Clk_ccdread_nom has been enabled for the F-CAM.
        - Boolean indicating whether or not the Clk_ccdread_red has been enabled for the F-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_clock_status()


def get_n_cam_sync_quality() -> (IntSwitch, IntSwitch):
    """ Return the status for the synchronisation generator for the N-CAM.

    For the Clk_50MHz and Clk_ccdread clocks for the N-CAM a boolean is returned with the following meaning:

        - 1: Synchronisation failure detected;
        - 0: No synchronisation failure detected.

    Returns:
        - Boolean indicating the status of the synchronisation generator for the Clk_50MHz clock for the N-CAM.
        - Boolean indicating the status of the synchronisation generator for the Clk_ccdread clock for the N-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_n_cam_clock_quality()


def get_f_cam_sync_quality() -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
    """ Return the status for the synchronisation generator for the F-CAM.

    For the Clk_50MHz and Clk_ccdread clocks (both nominal and redundant) for the F-CAM a boolean is returned with
    the following meaning:

        - 1: Synchronisation failure detected;
        - 0: No synchronisation failure detected.

    Returns:
        - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_nom clock for the F-CAM.
        - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_red clock for the F-CAM.
        - Boolean indicating the status of the synchronisation generator for the Clk_ccdread_nom clock for the
          F-CAM.
        - Boolean indicating the status of the synchronisation generator for the Clk_ccdread_red clock for the
          F-CAM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_f_cam_clock_quality()


def get_svm_sync_status() -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
    """ Return the status for the synchronisation generator for the SVM.

    For the Clk_50MHz and Clk_heater clocks (both nominal and redundant) for the SVM a boolean is returned with
    the following meaning:

        - True: Synchronisation failure detected;
        - False: No synchronisation failure detected.

    Returns:
        - Boolean indicating whether or not the Clk_50MHz_nom clock has been enabled for the SVM.
        - Boolean indicating whether or not the Clk_50MHz_red clock has been enabled for the SVM.
        - Boolean indicating whether or not the Clk_heater_nom clock has been enabled for the SVM.
        - Boolean indicating whether or not the Clk_heater_red clock has been enabled for the SVM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_svm_clock_status()


def get_svm_sync_quality() -> (IntSwitch, IntSwitch, IntSwitch, IntSwitch):
    """ Return the status for the synchronisation generator for the SVM.

    For the Clk_50MHz and Clk_heater clocks (both nominal and redundant) for the SVM a boolean is returned with
    the following meaning:

        - True: Synchronisation failure detected;
        - False: No synchronisation failure detected.

    Returns:
        - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_nom clock for the SVM.
        - Boolean indicating the status of the synchronisation generator for the Clk_50MHz_red clock for the SVM.
        - Boolean indicating the status of the synchronisation generator for the Clk_heater_nom clock for the SVM.
        - Boolean indicating the status of the synchronisation generator for the Clk_heater_red clock for the SVM.
    """

    crio = GlobalState.setup.gse.aeu.crio.device
    reconnect(crio)

    return crio.get_svm_clock_quality()


@building_block
def selftest(loopback_option: LoopBack):
    """ Execute a self-test with the given loopback option.

    Args:
        - loopback_option: Loopback option to use for the self-test.
    """

    setup = GlobalState.setup

    # Switch of the sync pulses and power for the N-CAM

    if n_cam_is_syncing():

        n_cam_sync_disable()

    if n_cam_is_on():

        n_cam_swoff()

    # Switch of the sync pulses and power for the F-CAM

    if f_cam_is_syncing():

        f_cam_sync_disable()

    if f_cam_is_on():

        f_cam_swoff()

    crio: CRIOInterface = setup.gse.aeu.crio.device
    reconnect(crio)

    # Go to self-test mode

    crio.set_operating_mode(OperatingMode.SELFTEST)

    selftest_led_status = crio.get_led_status()["Selftest"]

    if not selftest_led_status:

        raise AEUError("The self-test LED should be on")

    # Set the loopback option

    crio.set_loopback_option(loopback_option=loopback_option)

    actual_loopback_option = crio.get_loopback_option()
    if actual_loopback_option != loopback_option:

        raise AEUError(f"The loopback option should be {LOOPBACK[loopback_option]} but is "
                       f"{LOOPBACK[actual_loopback_option]}")

    # Wait for the self-test to finish

    wait_until(crio.get_led_status["Standby"])

    # Log the result of the self-test

    selftest_result = crio.get_selftest_result()
    LOGGER.info(f"Self-test finished.  Result: {SELFTEST_RESULT[selftest_result]}")


@building_block
def selftest_normal():
    """ Execute a self-test without loopback."""

    selftest(LoopBack.NO_LOOPBACK)


@building_block
def selftest_f_cam_nom():
    """ Execute a self-test with loopback F-CAM nominal."""

    selftest(LoopBack.F_CAM_NOM)


@building_block
def selftest_f_cam_red():
    """ Execute a self-test with loopback F-CAM redundant."""

    selftest(LoopBack.F_CAM_RED)


@building_block
def selftest_n_cam():
    """ Execute a self-test with loopback N-CAM."""

    selftest(LoopBack.N_CAM)


@building_block
def selftest_svm_nom():
    """ Execute a self-test with loopback SVM CAM TCS nominal."""

    selftest(LoopBack.SVM_NOM)


@building_block
def selftest_svm_red():
    """ Execute a self-test with loopback SVM CAM TCS redundant."""

    selftest(LoopBack.SVM_RED)


def n_cam_psu_ovp_recovery():
    """ Recovery from PSU Over-Voltage for the N-CAM."""

    for psu_index in range(1, 7):

        psu = PSUProxy(psu_index)

        psu.clear_alarms()
        psu.set_output_status(IntSwitch.ON)

    crio = CRIOProxy()

    crio.set_n_cam_secondary_power_status(IntSwitch.ON)
    LOGGER.info(crio.get_n_cam_voltage_quality())


def f_cam_psu_ovp_recovery():
    """ Recovery from PSU Over-Voltage for the F-CAM."""

    for psu_index in range(1, 7):

        psu = PSUProxy(psu_index)

        psu.clear_alarms()
        psu.set_output_status(IntSwitch.ON)

    crio = CRIOProxy()

    crio.set_f_cam_secondary_power_status(IntSwitch.ON)
    LOGGER.info(crio.get_f_cam_voltage_quality())
