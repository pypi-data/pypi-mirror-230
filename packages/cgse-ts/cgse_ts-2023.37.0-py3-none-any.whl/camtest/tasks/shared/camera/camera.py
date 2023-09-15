import os
import time
from enum import Enum
from pathlib import Path

from gui_executor.exec import exec_ui, Directory
from gui_executor.utypes import Callback

from camtest import end_observation
from camtest import start_observation
from camtest.commanding import aeu, dpu
from camtest.tasks.shared.camera import environments
from egse.aeu.aeu import CRIOProxy, PSUProxy, is_aeu_cs_active
from egse.aeu.aeu import IntSwitch
from egse.config import find_file
from egse.dpu import DPUInterface
from egse.dpu.dpu_cs import is_dpu_cs_active
from egse.exceptions import Abort
from egse.settings import Settings
from egse.setup import Setup
from egse.setup import submit_setup
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "4 — Camera"

ICON_PATH = Path(__file__).parent.resolve() / "icons/"
DATA_PATH = Path(os.environ.get("PLATO_DATA_STORAGE_LOCATION"))

AEU_SETTINGS = Settings.load("AEU Control Server")


@exec_ui(display_name="Switch ON",
         icons=(ICON_PATH / "n1-camera-swon.svg", ICON_PATH / "n1-camera-swon-selected.svg"),
         input_request=("[Y/n] ?",))
def switch_on_camera(environment: Callback(environments, name="Test environment") = None, hk_frequency: float = 4.0,
                     split_ccd_sides: bool = False):
    """ Camera switch-on procedure.

    This procedure entails the following steps:
        - Power on the N-cam + enable the sync signals, with the following parameters:
            - image cycle time: 25s
            - nominal heater clock: on
            - redundant heater : off
        - Set N-FEE FPGA defaults;
        - Go to STAND-BY mode;
        - Go to DUMP mode (external sync);
        - Acquire & dump (this finishes in DUMP mode (external sync)).  During this step (actually from 3s before till
          3s after this step), the frequency of the AEU cRIO and PSU HK will be changed to the given frequency.

    Prerequisites (to be included in the procedure):
        - Core services running;
        - DPU Control Server running;
        - All AEU Control Servers running;
        - N-FEE HK process running;
        - FITS generation process running.

    The following values are hard-coded for the acquire & dump:
        - num_cycles (5): Number images to acquire. If zero, images will continue to be acquired until the FEE is set to
                          STANDBY or DUMP mode again
        - row_start (0) : First row to read out
        - row_end (4509) : Last row to read out (inclusive)
        - rows_final_dump (0): Number of rows for the clear-out after the readout
        - ccd_order ([1, 2, 3, 4]): Array of four integers, indicating in which order the CCDs should be read
        - ccd_side (BOTH): CCD side for which to acquire data

    After each step, the user is prompted to check whether the system is in the correct state, so he/she
    can decide to continue with the camera start-up procedure or to interrupt it.

    Args:
        - environment: Indicates whether testing at ambient or under TVAC (relevant for the power consumption checks)
        - hk_frequency: Frequency at which to acquire AEU HK (cRIO + PSUs) during the acquire & dump [Hz]
    """

    from camtest.tasks.shared.camera.aeu import print_power_consumption
    
    try:
        not_all_cs_active = False

        if not is_dpu_cs_active():
            print("The DPU Control Server must be running for the camera switch-on")
            not_all_cs_active = True
        if not is_aeu_cs_active(name="CRIO"):
            print("The AEU cRIO Control Server must be running for the camera switch-on")
            not_all_cs_active = True
        for psu_index in range(1, 7):
            if not is_aeu_cs_active(name=f"PSU{psu_index}"):
                print(f"The AEU PSU{psu_index} Control Server must be running for the camera switch-on")
                not_all_cs_active = True
        for awg_index in range(1, 3):
            if not is_aeu_cs_active(name=f"AWG{awg_index}"):
                print(f"The AEU AWG{awg_index} Control Server must be running for the camera switch-on")
                not_all_cs_active = True

        if not_all_cs_active:
            raise Abort("Camera switch-on aborted because not all required Control Servers were active (DPU + AEU).  "
                        "Check the PM UI.")

        start_observation("Camera switch-on procedure")

        if not aeu.n_cam_is_on():
            print("\n***********************")
            print("Switching on the N-AEU...")
            aeu.n_cam_swon()
            aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=IntSwitch.ON, svm_red=IntSwitch.OFF)

            print("Check in the AEU UI that the six N-cam power lines are enabled and the sync signals are being sent, "
                  "and in the DPU UI that you are in ON mode (N-FEE Mode == ON_MODE).  Note that it can take up to "
                  "25s for the N-FEE to changes modes. \n In the next step we will check the AEU cRIO voltages and "
                  "currents.")

            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure...")
                return

        if aeu.n_cam_is_on():
            print("***********************")
            # Temporarily increase the AEU HK frequency

            print(f"Increasing the AEU HK frequency (cRIO + PSU) to {hk_frequency}Hz...")

            with CRIOProxy() as crio:
                with crio.get_service_proxy() as service_proxy:
                    service_proxy.set_hk_frequency(hk_frequency)
            for psu_index in range(1, 7):
                with PSUProxy(psu_index) as psu:
                    with psu.get_service_proxy() as service_proxy:
                        service_proxy.set_hk_frequency(hk_frequency)

            time.sleep(3)

        print("\n***********************")
        print("Syncing the N-FEE register map...")
        dpu_if: DPUInterface = GlobalState.setup.camera.dpu.device
        dpu_if.n_fee_sync_register_map()

        if dpu.n_cam_is_on_mode():
            print("\n***********************")
            print("The N-FEE is in ON mode.")

            print("\n***********************")
            print("Checking power consumption for ON mode...")
            print_power_consumption(environment=environment)
            print("Check the AEU cRIO voltages and currents in the table above.  All voltages should be within their "
                  "nominal range. \nIn the next step we will set the N-FEE FPGA defaults.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure...")
                return

            print("\n***********************")
            if "fpga_defaults" in GlobalState.setup.camera.fee:
                print("Setting the N-FEE FPGA defaults...")
                dpu.n_fee_set_fpga_defaults()
                print("Check above that the N-FEE FPGA parameters have been set correctly (below the table with the "
                      "parameters that have changed). \nIn the next step, we will go to STAND-BY mode.")
            else:
                print("Skipping setting the N-FEE FPGA default (info not present in setup)...  Only applicable for EM! "
                      "\nIn the next step, we will go to STAND-BY mode.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure.")
                return

            print("***********************")
            print("Going to STAND-BY mode...")
            dpu.n_cam_to_standby_mode()
            print("Check in the DPU UI that you are in STAND-BY mode (N-FEE MODE == STAND_BY_MODE).  Note that it can "
                  "take up to 25s for the N-FEE to changes modes. \nIn the next step we will check the AEU cRIO "
                  "voltages and currents.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure.")
                return

        if dpu.n_cam_is_standby_mode():
            print("***********************")
            print("The N-FEE is in STAND-BY mode.")

            print("***********************")
            print("Checking power consumption for STAND-BY mode...")
            print_power_consumption(environment=environment)
            print("Check the AEU cRIO voltages and currents in the table above.  All voltages should be within their "
                  "nominal range. \nIn the next step, we will go to DUMP mode.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure...")
                return

            print("\n***********************")
            print("Going to DUMP mode...")
            dpu.n_cam_to_dump_mode()
            print("Check in the DPU UI that you are in DUMP mode (N-FEE Mode == FULL_IMAGE_MODE and DUMP Mode = "
                  "True).  Note that it can take up to 25s for the N-FEE to changes modes. \nIn the next step we will "
                  "check the AEU cRIO voltages and currents.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure...")
                return

        if dpu.n_cam_is_dump_mode():
            print("***********************")
            print("The N-FEE is in DUMP mode...")

            print("***********************")
            print("Checking power consumption for FULL-IMAGE mode...")
            print_power_consumption(environment=environment)
            print("Check the AEU cRIO voltages and currents in the table above.  All voltages should be within their "
                  "nominal range.\nIn the next step, we will execute an acquire-and-dump observation.")
            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure.")
                return

            print("***********************")
            print("Make sure it is dark in the cleanroom and that the camera is in a closed tent. \nWe will execute "
                  "an acquire-and-dump observation.")

            response = input("Continue with the camera switch-on procedure [Y/n] ?")
            if response.lower() != "y":
                print("Exiting the camera switch-on procedure...")
                return

            if split_ccd_sides:
                dpu.n_cam_acquire_and_dump(num_cycles=5, row_start=0, row_end=4539,
                                           rows_final_dump=0, ccd_order=[1, 2, 3, 4],
                                           ccd_side="E")  # At the end, you are in DUMP mode
                dpu.n_cam_acquire_and_dump(num_cycles=5, row_start=0, row_end=4539,
                                           rows_final_dump=0, ccd_order=[1, 2, 3, 4],
                                           ccd_side="F")  # At the end, you are in DUMP mode
            else:
                dpu.n_cam_acquire_and_dump(num_cycles=5, row_start=0, row_end=4539,
                                           rows_final_dump=0, ccd_order=[1, 2, 3, 4],
                                           ccd_side="BOTH")  # At the end, you are in DUMP mode
            time.sleep(3)
    finally:
        # Reset the AEU HK frequency

        if not not_all_cs_active:
            print("Resetting the AEU HK frequency (cRIO + PSU)...")

            with CRIOProxy() as crio:
                with crio.get_service_proxy() as service_proxy:
                    service_proxy.set_hk_frequency(1. / AEU_SETTINGS["CRIO"]["HK_DELAY"])
            for psu_index in range(1, 7):
                with PSUProxy(psu_index) as psu:
                    with psu.get_service_proxy() as service_proxy:
                        service_proxy.set_hk_frequency(1. / AEU_SETTINGS[f"PSU{psu_index}"]["HK_DELAY"])

            end_observation()


@exec_ui(display_name="Switch OFF",
         icons=(ICON_PATH / "n1-camera-swoff.svg", ICON_PATH / "n1-camera-swoff-selected.svg"),
         input_request=("[Y/n] ?",))
def switch_off_camera():
    """ Camera switch-off procedure.

    This procedure entails the following steps:
        - Go to STAND-BY mode;
        - Go to ON mode;
        - Disable the sync signals and power off the N-cam.

    After each step, the user is prompted to check whether the system is in the correct state, so he/she
    can decide to continue with the camera shut-down procedure or to interrupt it.
    """
    try:
        not_all_cs_active = False

        if not is_dpu_cs_active():
            print("The DPU Control Server must be running for the camera switch-off")
            not_all_cs_active = True
        if not is_aeu_cs_active(name="CRIO"):
            print("The AEU cRIO Control Server must be running for the camera switch-of")
            not_all_cs_active = True
        for psu_index in range(1, 7):
            if not is_aeu_cs_active(name=f"PSU{psu_index}"):
                print(f"The AEU PSU{psu_index} Control Server must be running for the camera switch-off")
                not_all_cs_active = True
        for awg_index in range(1, 3):
            if not is_aeu_cs_active(name=f"AWG{awg_index}"):
                print(f"The AEU AWG{awg_index} Control Server must be running for the camera switch-off")
                not_all_cs_active = True

        if not_all_cs_active:
            raise Abort("Camera switch-off aborted because not all required Control Servers were active (DPU + AEU).  "
                        "Check the PM UI.")

        start_observation("Camera switch-off procedure")

        if not aeu.n_cam_is_on():
            return

        if dpu.n_cam_is_dump_mode():
            print("\n***********************")
            print("Going to STAND-BY mode...")
            dpu.n_cam_to_standby_mode()
            print("Check in the DPU UI that you are in STAND-BY mode (N-FEE Mode == STAND_BY_MODE). Note that it can "
                  "take up to 25s for the N-FEE to changes modes. \nIn the next step, we will go to ON mode.")
            response = input("Continue with the camera switch-off procedure [Y/n] ? ")
            if response.lower() != "y":
                print("Exiting the camera switch-off procedure...")
                return

        if dpu.n_cam_is_standby_mode():
            print("\n***********************")
            print("Going to ON mode...")
            dpu.n_cam_to_on_mode()
            print("Check in the DPU UI that you are in ON mode (N-FEE Mode == ON_MODE). \nIn the next step, we will "
                  "switch off the N-AEU.")
            response = input("Continue with the camera switch-off procedure [Y/n] ? ")
            if response.lower() != "y":
                print("Exiting the camera switch-off procedure...")
                return

        if dpu.n_cam_is_on_mode():
            print("***********************")
            print("Switching off the N-AEU...")
            aeu.n_cam_sync_disable()
            aeu.n_cam_swoff()

    finally:
        if not not_all_cs_active:
            end_observation()


@exec_ui(display_name="SFT Analysis")
def sft_analysis(
        obsid: int = None,
        data_dir: Directory = DATA_PATH / "obs",
        output_dir: Directory = DATA_PATH / "analysed/pngs/",
        verbose: bool = True,
        showplots: bool = True
):
    """
    sft_analysis

    Inputs:
        obsid: int = None                                       mandatory
        data_dir: Directory = DATA_PATH / "obs"                 optional.
        output_dir: Directory = DATA_PATH / "analysed/pngs/",   optional.
        verbose: bool = True,                                   optional. Prints the numerical ouputs
        showplots: bool = True                                  optional. Displays the plots

    """
    from camtest.analysis.analysis_SFT import analysis_SFT_HK

    setup = None
    camera = None

    data_dir = f"{str(data_dir)}/"  # make sure the folder name ends with a '/'
    output_dir = f"{str(output_dir)}/"  # make sure the folder name ends with a '/'

    analysis_SFT_HK(obsid=obsid, camera=camera, data_dir=data_dir, output_dir=output_dir, setup=setup, verbose=verbose,
                    showplots=showplots)

class CSL_SITE_ID(str, Enum):

    CSL = "CSL"
    CSL1 = "CSL1"
    CSL2 = "CSL2"

@exec_ui(display_name="Copy camera information")
def copy_cam_info(csl_site: CSL_SITE_ID = CSL_SITE_ID.CSL, setup_id: int = None):
    """ Copy the camera and telemetry block from the given CSL setup into the current setup and submit it.

    Make sure you have loaded the latest setup for your TH before executing this task.  It will create a new setup
    (with the updated information), which will be automatically pushed to the plato-cgse-conf directory.

    Please, check that the returned response really is a Setup object and not a Failure object.  In the latter case,
    something went wrong when submitting the new setup.

    When you want to load the new setup in your Python session, use:
        >>> setup = GlobalState.setup

    Args:
        - csl_site: CSL cleanroom in which the incoming camera was aligned (CSL1/CSL2).  To be provided in the datapack.
        - setup_id: Last setup at the given cleanroom for the incoming camera.

    Returns: Response to submitting the modified setup.
    """

    csl_setup_dir = str((Path(os.environ["PLATO_CONF_DATA_LOCATION"]) / ".." / ".." / csl_site.value / "conf").
                        resolve())
    print(f"CSL setup dir: {csl_setup_dir}")
    csl_setup_filename = find_file(name=f"SETUP_{csl_site.value}_{setup_id:05d}_*_*.yaml", root=csl_setup_dir)

    if csl_setup_filename is None:
        print(f"Could not find setup {setup_id} for {csl_site.value}")
        return

    print(f"CSL setup filename: {csl_setup_filename.name}")
    csl_setup = Setup.from_yaml_file(csl_setup_filename)

    current_setup = GlobalState.setup

    current_setup.camera = csl_setup.camera
    print(f"Updating camera information of {current_setup.site_id} setup {current_setup.get_id()}")

    current_setup["telemetry"] = csl_setup.telemetry
    print(f"Updating telemetry information of {current_setup.site_id} setup {current_setup.get_id()}")

    response = submit_setup(setup=current_setup, description=f"Copy camera and telemetry info for "
                                                             f"{csl_setup.camera.ID} from {csl_site.value} setup "
                                                             f"{setup_id}")
    return response
