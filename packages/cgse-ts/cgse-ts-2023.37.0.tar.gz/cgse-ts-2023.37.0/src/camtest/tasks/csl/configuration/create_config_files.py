import os
import string
from pathlib import Path

from gui_executor.exec import exec_ui, FilePath, Directory
from gui_executor.utypes import Callback

from camtest.tasks.csl.configuration import camera_ids
from egse.config import find_files
from egse.setup import NavigableDict

UI_MODULE_DISPLAY_NAME = "1 - Create configuration / calibration files"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

ORIGIN = "N-FEE-HK"
AMBIENT_CCD_CAL_RESISTANCE_TO_TEMPERATURE = [0.00000000015243, -0.000000028183, -0.000004826, 0.0025859, 2.2228, -242.02]


class SensorCalibration(NavigableDict):

    def __init__(self, nav_dict: NavigableDict = None, camera_id: str = None):
        super().__init__(nav_dict or {})
        self.set_private_attribute("_camera_id", camera_id)

    def to_yaml_file(self, yaml_filename: str = None, ini_filename: str = None):

        print(f"Saving N-FEE sensor calibration to {yaml_filename}")

        with Path(yaml_filename).open("w") as fd:

            camera_id = self.get_private_attribute("_camera_id")

            fd.write(f"# N-FEE FPGA sensor calibration for {camera_id}\n")
            fd.write(f"# Reference: {Path(ini_filename).stem}\n")
            fd.write("# Ambient calibration for CCD temperatures discussed in #293\n")
            fd.write(f"# CCD handling jigs taken from \n")

            self._save(fd, indent=0)


@exec_ui(display_name="N-FEE FPGA defaults", use_kernel=True)
def nfee_fpga_defaults(camera_id: Callback(camera_ids, name="Camera selection") = None,
                       filename: FilePath = "nfee_fpga_defaults_camera.ini",
                       output_folder: Directory =
                       Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"):
    """ Create YAML file with the N-FEE FPGA defaults from the given INI file for the given camera.

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Full path of the INI file with the N-FEE FPGA defaults for the given camera
        - output_folder: Full path to the folder in which the N-FEE FPGA defaults YAML file should be stored

    Returns: Full path of the YAML file with the N-FEE FPGA defaults
    """

    ini_file = open(filename)

    yaml_filename = Path(output_folder / f"nfee_fpga_defaults_{camera_id}.yaml")
    yaml_file = open(yaml_filename, "w")

    yaml_file.write(f"# N-FEE FPGA defaults for {camera_id}\n")
    yaml_file.write(f"# Reference: {Path(filename).stem}\n")

    text_list = ini_file.readlines()
    for line in text_list:

        if line.startswith("Reg_"):
            reg_entry_name, value = line.split(" = ")
            _, entry_index = reg_entry_name.split("_")
            value = value.strip("\n").strip("\"")

            yaml_file.write(f"reg_{entry_index}_config: \'{value}\'\n")

    ini_file.close()
    yaml_file.close()

    return yaml_filename


@exec_ui(display_name="N-FEE sensor calibration", use_kernel=True)
def nfee_sensor_calibration(camera_id: Callback(camera_ids, name="camera_id") = None,
                            filename: FilePath = "nfee_sensor_calibration_camera.ini",
                            ccd1_handling_jig: str = "HJ...", ccd2_handling_jig: str = "HJ...",
                            ccd3_handling_jig: str = "HJ...", ccd4_handling_jig: str = "HJ...",
                            output_folder: Directory =
                            Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"):
    """ Create YAML file with the N-FEE sensor calibration from the given INI file for the given camera.

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Full path of the INI file with the N-FEE sensor calibration for the given camera
        - output_folder: Full path to the folder in which the N-FEE sensor calibration YAML file should be stored
        - ccd1_handling_jig: Handling jig for CCD1
        - ccd2_handling_jig: Handling jig for CCD2
        - ccd3_handling_jig: Handling jig for CCD3
        - ccd4_handling_jig: Handling jig for CCD4

    Returns: Full path of the YAML file with the N-FEE sensor calibration
    """

    pattern = f"nfee_sensor_calibration_{camera_id}_v*.yaml"
    version = len(list(find_files(pattern=pattern, root=output_folder))) + 1
    yaml_filename = Path(output_folder / f"nfee_sensor_calibration_{camera_id}_v{version}.yaml")

    ini_file = open(filename)
    reached_start = False
    while not reached_start:
        line = ini_file.readline()
        reached_start = "HK_cal" in line
    line = ini_file.readline()

    ini_dict = {}

    while "=" in line:
        try:
            mssl_name, value = line.split(" = ")
            mssl_name = mssl_name[22:]  # Throw away "HK transfer functions."
            value = float(value.strip("\n").strip(" ").strip("\""))
            ini_dict[mssl_name] = value
            line = ini_file.readline()
        except ValueError:
            pass    # One line too far

    ini_file.close()

    # Temperatures

    temperatures = dict()

    resistance_to_temperature_cvd = {
        "method": "callendar_van_dusen",
        "standard": "EN60751",
        "ref_resistance": 1000
    }

    tou_trp_pt1000 = dict()
    sensor_names = ["NFEE_TOU_TRP5", "NFEE_TOU_TRP10", "NFEE_TOU_TRP8", "NFEE_TOU_TRP21", "NFEE_TOU_TRP31",
                    "NFEE_TOU_TRP41"]
    tou_trp_pt1000["sensor_names"] = sensor_names

    for index in range(len(sensor_names)):
        tou_sense_index = index + 1
        tou_trp_pt1000_item = {
            "counts_to_resistance_gain": ini_dict[f"TOU {tou_sense_index}.a"],
            "counts_to_resistance_offset": ini_dict[f"TOU {tou_sense_index}.b"],
            "resistance_to_temperature": resistance_to_temperature_cvd
        }

        tou_trp_pt1000[sensor_names[index]] = tou_trp_pt1000_item
    temperatures["TOU_TRP_PT1000"] = tou_trp_pt1000

    ccd_pt1000 = dict()
    ccd_pt1000["sensor_names"] = ["NFEE_T_CCD1", "NFEE_T_CCD2", "NFEE_T_CCD3", "NFEE_T_CCD4", "NFEE_T_CCD1_AMB",
                                  "NFEE_T_CCD2_AMB", "NFEE_T_CCD3_AMB", "NFEE_T_CCD4_AMB"]
    ccd_handling_jigs = [None, ccd1_handling_jig, ccd2_handling_jig, ccd3_handling_jig, ccd4_handling_jig]

    for ccd_index in range(1, 5):
        resistance_to_temperature_coefficients_tvac = []
        for fit_index in range(5, 0, -1):
            resistance_to_temperature_coefficients_tvac.append(ini_dict[f"CCD {ccd_index} fit.x{fit_index}"])

        ccd_pt1000_item_tvac = {
            "handling_jig": ccd_handling_jigs[ccd_index],
            "counts_to_resistance_gain": ini_dict[f"CCD {ccd_index}.a"],
            "counts_to_resistance_offset": ini_dict[f"CCD {ccd_index}.b"],
            "resistance_to_temperature": {
                "method": "polynomial",
                "resistance_to_temperature_coefficients": resistance_to_temperature_coefficients_tvac
            }
        }
        ccd_pt1000[f"NFEE_T_CCD{ccd_index}"] = ccd_pt1000_item_tvac

        ccd_pt1000_item_amb = {
            "handling_jig": ccd_handling_jigs[ccd_index],
            "counts_to_resistance_gain": ini_dict[f"CCD {ccd_index}.a"],
            "counts_to_resistance_offset": ini_dict[f"CCD {ccd_index}.b"],
            "resistance_to_temperature": {
                "divide_resistance_by": 10.0,
                "method": "polynomial",
                "resistance_to_temperature_coefficients": AMBIENT_CCD_CAL_RESISTANCE_TO_TEMPERATURE
            }
        }
        ccd_pt1000[f"NFEE_T_CCD{ccd_index}_AMB"] = ccd_pt1000_item_amb

    temperatures["CCD_PT1000"] = ccd_pt1000

    board_pt1000 = dict()
    sensor_names = ["NFEE_T_PCB1", "NFEE_T_PCB2", "NFEE_T_ADC", "NFEE_T_CDS", "NFEE_T_ANALOG"]
    board_pt1000["sensor_names"] = sensor_names

    for index in range(len(sensor_names)):
        trp_sense_index = index + 1
        board_pt1000_item = {
            "counts_to_resistance_gain": ini_dict[f"PRT {trp_sense_index}.a"],
            "counts_to_resistance_offset": ini_dict[f"PRT {trp_sense_index}.b"],
            "resistance_to_temperature": resistance_to_temperature_cvd
        }

        board_pt1000[sensor_names[index]] = board_pt1000_item

    temperatures["BOARD_PT1000"] = board_pt1000

    board_isl71950 = dict()
    sensor_names = ["NFEE_T_PCB3", "NFEE_T_PCB4"]
    board_isl71950["sensor_names"] = sensor_names

    for index in range(len(sensor_names)):
        sense_index = string.ascii_uppercase[index]
        board_isl71950_item = {
            "counts_to_temperature_gain": ini_dict[f"T_{sense_index}.a"],
            "counts_to_temperature_offset": ini_dict[f"T_{sense_index}.b"]
        }
        board_isl71950[sensor_names[index]] = board_isl71950_item

    temperatures["BOARD_ISL71590"] = board_isl71950

    # Supply voltages

    supply_voltages = dict()

    ccd_voltages = ["VOD_E", "VOD_F", "VOG", "VRD_E", "VRD_F", "VDD", "VGD"]

    for ccd_index in range(1, 5):
        for ccd_voltage in ccd_voltages:
            mssl_name = f"CCD{ccd_index}_{ccd_voltage}_MON"

            try:
                supply_voltage_item = {
                    "gain": ini_dict[f"{mssl_name}.a"],
                    "offset": ini_dict[f"{mssl_name}.b"],
                }
            except KeyError:
                supply_voltage_item = {
                    "gain": ini_dict[f"{mssl_name} 2.a"],
                    "offset": ini_dict[f"{mssl_name} 2.b"],
                }
            supply_voltages[f"NFEE_CCD{ccd_index}_{ccd_voltage}"] = supply_voltage_item

    matching_names = ["VCCD", "VRCLK", "VICLK", "IG_HI", "VCCD_R", "VCLK_R", "VAN1_R", "VAN2_R", "VAN3_R", "3V3B", "2V5A", "3V3D", "2V5D", "1V8D", "1V5D", "5VREF"]

    for matching_name in matching_names:
        try:
            supply_voltage_item = {
                "gain": ini_dict[f"{matching_name}.a"],
                "offset": ini_dict[f"{matching_name}.b"],
            }
        except KeyError:
            supply_voltage_item = {
                "gain": ini_dict[f"{matching_name} .a"],
                "offset": ini_dict[f"{matching_name} .b"],
            }

        supply_voltages[f"NFEE_{matching_name}"] = supply_voltage_item

    supply_voltages["NFEE_5VB_NEG"] = {
        "gain": ini_dict["-5VB.a"],
        "offset": ini_dict["-5VB.b"]
    }
    supply_voltages["NFEE_VDIG"] = {
        "gain": ini_dict["VDIG_R.a"],
        "offset": ini_dict["VDIG_R.b"]
    }

    sensor_calibration = SensorCalibration({
        "temperatures": temperatures,
        "supply_voltages": supply_voltages
    }, camera_id=camera_id)

    sensor_calibration.to_yaml_file(yaml_filename=yaml_filename, ini_filename=filename)

    return yaml_filename


    # for egse_name in ccd_pt1000["sensor_names"]:
    #     ccd_pt1000_item = dict()
    #
    #     resistance_to_temperature_coefficients = []
    #     for index in range(5, -1, -1):
    #         resistance_to_temperature_coefficients.append(ini_dict[f"{mssl_name} fit.x{index}"])
    #
    #     ccd_pt1000_item["handling_jig"] = ccd_handling_jigs[int(egse_name[-1])]
    #     ccd_pt1000_item["counts_to_resistance_gain"] = ini_dict[f"{mssl_name}.a"]
    #     ccd_pt1000_item["counts_to_resistance_offset"] = ini_dict[f"{mssl_name}.b"]
    #     ccd_pt1000_item["resistance_to_temperature"] = {
    #         "method": "polynomial",
    #         "resistance_to_temperature_coefficients": resistance_to_temperature_coefficients
    #     }
    #
    #     ccd_pt1000[egse_name] = ccd_pt1000_item



    # # Translation MSSL -> EGSE names
    #
    # hk_name_mapping = read_conversion_dict(ORIGIN, use_site=False)
    #
    # sensor_calibration = dict()
    #
    # # Temperatures
    #
    # temperatures = dict()
    #
    # resistance_to_temperature = {
    #     "method": "callendar_van_dusen",
    #     "standard": "EN60751",
    #     "ref_resistance": 1000
    # }
    #
    # tou_trp_pt1000 = dict()
    # tou_trp_pt1000["sensor_names"] = ["NFEE_TOU_TRP5", "NFEE_TOU_TRP10", "NFEE_TOU_TRP8", "NFEE_TOU_TRP21",
    #                                   "NFEE_TOU_TRP31", "NFEE_TOU_TRP41"]
    #
    # for egse_name in tou_trp_pt1000["sensor_names"]:
    #     mssl_name = hk_name_mapping[egse_name]
    #
    #     tou_trp_pt1000_item = dict()
    #     tou_trp_pt1000_item["counts_to_resistance_gain"] = ini_dict[f"{mssl_name}.a"]
    #     tou_trp_pt1000_item["counts_to_resistance_offset"] = ini_dict[f"{mssl_name}.b"]
    #     tou_trp_pt1000_item["resistance_to_temperature"] = resistance_to_temperature
    #
    #     tou_trp_pt1000[egse_name] = tou_trp_pt1000_item
    #
    # temperatures["TOU_TRP_PT1000"] = tou_trp_pt1000
    #
    # ccd_pt1000 = dict()
    # ccd_pt1000["sensor_names"] = ["NFEE_T_CCD1", "NFEE_T_CCD2", "NFEE_T_CCD3", "NFEE_T_CCD4"]
    #
    # for egse_name in ccd_pt1000["sensor_names"]:
    #     ccd_pt1000_item = dict()
    #
    #     resistance_to_temperature_coefficients = []
    #     for index in range(5, -1, -1):
    #         resistance_to_temperature_coefficients.append(ini_dict[f"{mssl_name} fit.x{index}"])
    #
    #     ccd_pt1000_item["handling_jig"] = ccd_handling_jigs[int(egse_name[-1])]
    #     ccd_pt1000_item["counts_to_resistance_gain"] = ini_dict[f"{mssl_name}.a"]
    #     ccd_pt1000_item["counts_to_resistance_offset"] = ini_dict[f"{mssl_name}.b"]
    #     ccd_pt1000_item["resistance_to_temperature"] = {
    #         "method": "polynomial",
    #         "resistance_to_temperature_coefficients": resistance_to_temperature_coefficients
    #     }
    #
    #     ccd_pt1000[egse_name] = ccd_pt1000_item
    #
    # temperatures["CCD_PT1000"] = ccd_pt1000
    #
    # board_pt1000 = dict()
    # board_pt1000["sensor_names"] = ["NFEE_T_PCB1", "NFEE_T_PCB2", "NFEE_T_ADC", "NFEE_T_CDS", "NFEE_T_ANALOG"]
    #
    # for egse_name in board_pt1000["sensor_names"]:
    #     mssl_name = hk_name_mapping[egse_name]
    #
    #     board_pt1000_item = dict()
    #
    #     board_pt1000_item["counts_to_resistance_gain"] = ini_dict[f"{mssl_name}.a"]
    #     board_pt1000_item["counts_to_resistance_offset"] = ini_dict[f"{mssl_name}.b"]
    #     board_pt1000_item["resistance_to_temperature"] = resistance_to_temperature
    #     board_pt1000[egse_name] = board_pt1000_item
    #
    # temperatures["BOARD_PT1000"] = board_pt1000
    #
    # board_isl71590 = dict()
    # board_isl71590["sensor_names"] = ["NFEE_T_PCB3", "NFEE_T_PCB4"]
    #
    # for egse_name in board_isl71590["sensor_names"]:
    #     mssl_name = hk_name_mapping[egse_name]
    #
    #     board_isl71590_item = dict()
    #     board_isl71590_item["counts_to_temperature_gain"] = ini_dict[f"{mssl_name}.a"]
    #     board_isl71590_item["counts_to_temperature_offset"] = ini_dict[f"{mssl_name}.b"]
    #     board_isl71590_item[egse_name] = board_isl71590_item
    #
    # temperatures["BOARD_ISL71590"] = board_isl71590
    #
    # sensor_calibration["temperatures"] = temperatures
    #
    # # Supply voltages
    #
    # supply_voltages = dict()
    #
    # for egse_name, mssl_name in hk_name_mapping.items():
    #
    #     if "_T" not in egse_name and "TRP" not in egse_name and egse_name.endswith("_RAW"):
    #
    #         item = {
    #             "gain": ini_dict[f"{mssl_name}.a"],
    #             "offset": ini_dict[f"{mssl_name}.b"]
    #         }
    #
    #         supply_voltages[egse_name] = item
    #
    # sensor_calibration["supply_voltages"] = supply_voltages
    #
    # print(NavigableDict(sensor_calibration))
    #
    # with open(yaml_filename, "w") as yaml_file:
    #     yaml.dump(sensor_calibration, yaml_file, default_flow_style=False)
    #
    # return yaml_filename
