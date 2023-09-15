import os
from math import atan2, degrees
from pathlib import Path
from statistics import mean
from typing import List

import numpy as np
import pandas
from gui_executor.exec import exec_ui, FilePath
from gui_executor.utypes import Callback, FixedList
from numpy.polynomial import Polynomial
from scipy.optimize import curve_fit
from camtest.tasks.csl.configuration import camera_ids
from egse.exceptions import Abort
from egse.settings import Settings
from egse.setup import submit_setup
from egse.state import GlobalState
from rich.console import Console
from rich.table import Table

UI_MODULE_DISPLAY_NAME = "2 - Include information in setup"
SITE_ID = Settings.load("SITE").ID

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


def hexapod_ids() -> List:
    """ List of hexapod identifiers."""

    if SITE_ID == "CSL1":
        return ["1A", "1B"]
    elif SITE_ID == "CSL2":
        return ["2A", "2B"]
    else:
        return []


def isostatic_plate_identifiers() -> List:
    """ List of isostatic-plate identifiers."""

    return ["1A", "1B", "2A", "2B"]


@exec_ui(display_name="Camera identifiers", use_kernel=True)
def camera_identification(camera_id: Callback(camera_ids, name="Camera selection") = None,
                          camera_serial_number: str = None,
                          tou_id: str = None, fee_id: str = None, fpa_id: str = None,
                          description: str = "Camera/FEE/FPA/FEE ID for ...  (#...)"):
    """ Ingest the camera identification in a new setup.

    The given information is ingested in the setup and the setup is submitted (meaning that it is automatically pushed
    to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - camera_serial_number: Serial number of the camera (to extract from
                                https://s2e2.cosmos.esa.int/confluence/pages/viewpage.action?pageId=171639593)
        - tou_id: Identifier for the TOU (to extract from the latest version of PLATO-INAF-PL-LI-0071)
        - fee_id: Identifier for the FEE (to extract from the latest version of PLATO-INAF-PL-LI-0071)
        - fpa_id: Identifier for the FPA (to extract from the latest version of PLATO-INAF-PL-LI-0071)
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the camera identifiers have been ingested.
    """

    check_description(camera_id, description)

    table = Table(title="Camera identifiers")
    table.add_column("Parameter")
    table.add_column("Value")

    table.add_row("Camera ID", camera_id)
    table.add_row("Camera serial number", camera_serial_number)
    table.add_row("TOU ID", tou_id)
    table.add_row("FEE ID", fee_id)
    table.add_row("FPA ID", fpa_id)

    console = Console(width=120)
    console.print(table)

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup

        setup.camera.ID = camera_id
        setup.camera.serial_number = camera_serial_number
        setup.camera.TOU.ID = tou_id
        setup.camera.fpa.ID = fpa_id
        setup.camera.fee.ID = fee_id

        return submit_setup(setup, description)

    else:
        print("Changes not included in the setup")


# class DistortionCoefficients(ListList):
#
#     def __init__(self, literals: List[Union[str, Callable]], defaults: List = None):
#         super().__init__(literals=literals, defaults=defaults, name="k1, k2, k3")
#
#     def get_widget(self):
#         return DistortionCoefficientsWidget(self)
#
#
# class DistortionCoefficientsWidget(ListListWidget):
#     def __init__(self, type_object: ListList):
#         super().__init__(type_object=type_object)
#
#     def _row(self, row_button: str, expand_default: bool = False):
#         widget = QWidget()
#
#         hbox = QHBoxLayout()
#
#         fields = []
#         for x, y in self._type_object:
#             if not expand_default:
#                 y = None
#             if x is bool:
#                 field = QCheckBox()
#                 from PyQt5.QtCore import Qt
#                 field.setCheckState(Qt.Checked if y is not None else Qt.Unchecked)
#             else:
#                 field = QLineEdit()
#                 field.setPlaceholderText(str(y) if y is not None else "")
#
#             if x is int:
#                 from PyQt5.QtGui import QIntValidator
#                 field.setValidator(QIntValidator())
#             elif x is float:
#                 from PyQt5.QtGui import QDoubleValidator
#                 field.setValidator(QDoubleValidator())
#
#             fields.append(field)
#             type_hint = QLabel(x if isinstance(x, str) else x.__name__)
#             type_hint.setStyleSheet("color: gray")
#             hbox.addWidget(field)
#             hbox.addWidget(type_hint)
#
#         hbox.setContentsMargins(0, 0, 0, 0)
#         widget.setLayout(hbox)
#
#         return widget, fields
#
#     def get_value(self) -> List:
#         return [
#             [
#                 self._cast_arg(f, t)
#                 for f, (t, d) in zip(field, self._type_object)
#             ] for field in self._rows
#         ][0]


# def fov(camera_id: Callback(camera_ids, name="str") = None,
#         distortion_coefficients: DistortionCoefficients([float, float, float], [0, 0, 0]) = None,
#         focal_length: float = None, description: str = "Field distortion & focal length for ..."):
@exec_ui(display_name="Field distortion & Focal length", use_kernel=True)
def fov(camera_id: Callback(camera_ids, name="Camera selection") = None, filename: FilePath = None,
        description: str = "Field distortion & focal length for ...  (#...)"):
    """ Ingest the field distortion information and focal length in a new setup.

    The given field distortion coefficients, the derived inverse field distortion coefficients, and the given focal
    length are ingested in the setup and the setup is submitted (meaning that it is automatically pushed to the
    repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Filename of the spreasheet attached to the FPA & TOU Metrology Summary Report (In Eclipse, look
                    for "PTO-EST-PL-RP").  The information will be extracted from PL-ALN-CSL-0215 and PL-ALN-CSL-0200.
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the field distortion information and the focal length have been ingested.
    """

    check_description(camera_id, description)

    fpa_sheet_name = pandas.ExcelFile(filename).sheet_names[2]
    pan = pandas.read_excel(filename, sheet_name=fpa_sheet_name, usecols="B:D", names=["k1", "k2", "k3"])

    focal_length_column = k1_column = pan["k1"].values
    k2_column = pan["k2"].values
    k3_column = pan["k3"].values

    ref_index = np.where(focal_length_column == "PL-ALN-CSL-0200")[0][0] + 3  # Table with the focal length
    focal_length = focal_length_column[ref_index]

    ref_index = np.where(focal_length_column == "PL-ALN-CSL-0215")[0][0] + 3  # Table with the field distortion coefficients
    distortion_coefficients = [k1_column[ref_index], k2_column[ref_index], k3_column[ref_index]]
    coefficients = [0, 0, 0, distortion_coefficients[0], 0, distortion_coefficients[1], 0, distortion_coefficients[2]]

    distortion_polynomial = Polynomial(coefficients)
    undistorted_radius = np.arange(0, 82, 0.1)
    distortion = distortion_polynomial(undistorted_radius / focal_length) * focal_length

    distorted_radius = undistorted_radius + distortion

    def inverse_distortion(distorted_radius, k1, k2, k3):
        normalized_radius = distorted_radius / focal_length
        return (k1 * pow(normalized_radius, 3) + k2 * pow(normalized_radius, 5) + k3 * pow(normalized_radius, 7)) * focal_length

    popt, _ = curve_fit(inverse_distortion, distorted_radius, -distortion)
    inverse_distortion_coefficients = list(popt)

    print(f"Field distortion coefficients: {distortion_coefficients}")
    print(f"Inverse field distortion coefficients: {inverse_distortion_coefficients}")
    print(f"Focal lengths: {focal_length}mm")

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup

        setup.camera.fov.distortion_coefficients = distortion_coefficients
        setup.camera.fov.inverse_distortion_coefficients = inverse_distortion_coefficients
        setup.camera.fov.focal_length_mm = focal_length

        return submit_setup(setup, description)
    else:
        print("Changes not included in the setup")


def angle_x_axis(start, end):
    """ Determine angle between straight line from start to and, and the x-axis.

    Args:
        - start: Starting point of the straight line (x, y)
        - end: Ending point of the straight line (x, y)

    Returns: Angle between the straight line from start to end, and the x-axis [degrees].
    """
    angle = degrees(atan2(end[1] - start[1], end[0] - start[0]))
    return (angle + 360) % 360


def angle_y_axis(start, end):
    """ Determine angle between straight line from start to and, and the y-axis.

    Args:
        - start: Starting point of the straight line (x, y)
        - end: Ending point of the straight line (x, y)

    Returns: Angle between the straight line from start to end, and the xyaxis [degrees].
    """
    angle = angle_x_axis(start, end) - 90
    return (angle + 360) % 360


@exec_ui(display_name="CCD positions", use_kernel=True)
def ccd(camera_id: Callback(camera_ids, name="Camera selection") = None, filename: FilePath = None,
        description: str = "CCD positions for ...  (#...)"):
    """ Ingest the CCD positions in a new setup.

    From the FPA tab in the given spreadsheet, the focal-plane coordinates of the four corners of the four CCDs is read,
    and from there we derive the orientation of the CCDs and their origin.  This information is ingested in the setup
    and the setup is submitted (meaning that it is automatically pushed to the repository and loaded into the
    Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Filename of the spreasheet attached to the FPA & TOU Metrology Summary Report (In Eclipse, look
                    for "PTO-EST-PL-RP").  The information will be extracted from PL-ALN-CSL-0050.
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the CCD positions have been ingested.
    """

    check_description(camera_id, description)

    sheet_names = pandas.ExcelFile(filename).sheet_names
    for sheet_name in sheet_names:
        if "FM" in sheet_name and "FPA" in sheet_name:
            break

    pan = pandas.read_excel(filename, sheet_name=sheet_name, usecols="B:F",
                            names=["reference", "bottom_left", "top_left", "top_right", "bottom_right"])

    reference = pan["reference"].values
    bottom_left_array = pan["bottom_left"].values
    top_left_array = pan["top_left"].values
    top_right_array = pan["top_right"].values
    bottom_right_array = pan["bottom_right"].values

    ref_index = np.where(reference == "PL-ALN-CSL-050")[0][0]   # Table with the corners of the CCDs

    orientation = []

    for ccd_index in range(4):

        x_row = ref_index + 3 + 2 * ccd_index

        ccd_bottom_left = bottom_left_array[x_row: x_row + 2]
        ccd_top_left = top_left_array[x_row: x_row + 2]
        ccd_top_right = top_right_array[x_row: x_row + 2]
        ccd_bottom_right = bottom_right_array[x_row: x_row + 2]

        ccd_angle1 = angle_y_axis(ccd_bottom_left, ccd_top_left)
        ccd_angle2 = angle_y_axis(ccd_bottom_right, ccd_top_right)
        ccd_angle3 = angle_x_axis(ccd_bottom_left, ccd_bottom_right)
        ccd_angle4 = angle_x_axis(ccd_top_left, ccd_top_right)

        ccd_avg_angle = mean([ccd_angle1, ccd_angle2, ccd_angle3, ccd_angle4])
        orientation.append(ccd_avg_angle)

    bottom_left_x = bottom_left_array[ref_index + 3: ref_index + 3 + 8: 2]
    bottom_left_y = bottom_left_array[ref_index + 3 + 1: ref_index + 3 + 8: 2]

    origin_offset_x = [bottom_left_x[0], bottom_left_y[1], -bottom_left_x[2], -bottom_left_y[3]]
    origin_offset_y = [bottom_left_y[0], -bottom_left_x[1], -bottom_left_y[2], bottom_left_x[3]]

    print(f"Origin offset (x-coordinate): {origin_offset_x}")
    print(f"Origin offset (y-coordinate): {origin_offset_y}")
    print(f"Orientation: {orientation}")

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup

        setup.camera.ccd.origin_offset_x = origin_offset_x
        setup.camera.ccd.origin_offset_y = origin_offset_y
        setup.camera.ccd.orientation = orientation

        return submit_setup(setup, description)
    else:
        print("Changes not included in the setup")


@exec_ui(display_name="FEE FPGA defaults", use_kernel=True)
def nfee_fpga_defaults(camera_id: Callback(camera_ids, name="Camera selection") = None, filename: FilePath = None,
                       description: str = "N-FEE FPGA defaults for ...  (#...)"):
    """ Ingest the N-FEE FPGA defaults in a new setup.

    In Sect. 1 (Create configuration / calibration files), we have already created a  YAML file with the N-FEE FPGA
    defaults.  This information is now ingested in the setup and the setup is submitted (meaning that it is
    automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Full path of the N-FEE FPGA defaults YAML file
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the N-FEE FPGA defaults have been ingested.
    """

    check_description(camera_id, description)
    check_filename(camera_id, filename.stem)

    nfee_conf_dir = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"

    if camera_id not in filename.stem:
        raise Abort(f"The camera name {camera_id} his not present in the filename of the N-FEE FPGA defaults.  Fix "
                    f"this and run the task again.")

    try:
        fpga_defaults = f"yaml//../../common/n-fee/{filename.relative_to(nfee_conf_dir)}"

        print(f"About to set setup.camera.fee.fpga_defaults to {fpga_defaults}")
        response = input("Submit setup [Y/n] ? ")

        if response.lower() == 'y':
            setup = GlobalState.setup
            setup.camera.fee.fpga_defaults = fpga_defaults

            return submit_setup(setup, description)
        else:
            print("Changes not included in the setup")
    except ValueError:
        Abort(f"N-FEE register and/or HK map for {camera_id} not found in {nfee_conf_dir}")


@exec_ui(display_name="N-FEE sensor calibration", use_kernel=True)
def nfee_sensor_calibration(camera_id: Callback(camera_ids, name="Camera selection") = None, filename: FilePath = None,
                            description: str = "FEE sensor calibration for ...  (#...)"):
    """ Ingest the N-FEE sensor calibration in a new setup.

    In Sect. 1 (Create configuration / calibration files), we have already created a  YAML file with the N-FEE sensor
    calibration.  This information is now ingested in the setup and the setup is submitted (meaning that it is
    automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Full path of the N-FEE sensor calibration YAML file
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the N-FEE sensor calibration has been ingested.
    """

    check_description(camera_id, description)
    check_filename(camera_id, filename.stem)

    nfee_conf_dir = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"

    try:
        sensor_calibration = f"yaml//../../common/n-fee/{filename.relative_to(nfee_conf_dir)}"

        print(f"About to set setup.camera.fee.calibration to {sensor_calibration}")
        response = input("Submit setup [Y/n] ? ")

        if response.lower() == 'y':

            setup = GlobalState.setup
            setup.camera.fee.calibration = sensor_calibration

            return submit_setup(setup, description)
        else:
            print("Changes not included in the setup")
    except ValueError:
        Abort(f"N-FEE sensor calibration for {camera_id} not found in {nfee_conf_dir}")


@exec_ui(display_name="N-FEE register & HK map", use_kernel=True)
def nfee_maps(camera_id: Callback(camera_ids, name="Camera selection") = None, register_map_filename: FilePath = None,
              hk_map_filename: FilePath = None, description: str = f"FEE register & HK map for ...  (#...)"):
    """ Ingest the N-FEE register and HK dmap in a new setup.

    In Sect. 1 (Create configuration / calibration files), we have already created YAML files with the N-FEE  register
    and HK maps.  This information is now ingested in the setup and the setup is submitted (meaning that it is
    automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - register_map_filename: Full path of the N-FEE register map YAML file
        - hk_map_filename: Full path of the N-FEE HK map YAML file
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the N-FEE register and HK map have been ingested.
    """

    check_description(camera_id, description)
    check_filename(camera_id, register_map_filename.stem)
    check_filename(camera_id, hk_map_filename.stem)

    nfee_conf_dir = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "n-fee"

    try:
        register_map = f"yaml//../../common/n-fee/{register_map_filename.relative_to(nfee_conf_dir)}"
        hk_map = f"yaml//../../common/n-fee/{hk_map_filename.relative_to(nfee_conf_dir)}"

        print(f"About to set setup.camera.fee.register_map to {register_map}")
        print(f"and setup.camera.fee.hk_map to {hk_map}")
        response = input("Submit setup [Y/n] ? ")

        if response.lower() == 'y':
            setup = GlobalState.setup

            setup.camera.fee.register_map = register_map
            setup.camera.fee.hk_map = hk_map

            return submit_setup(setup, description)
        else:
            print("Changes not included in the setup")
    except ValueError:
        Abort(f"N-FEE register and/or HK map for {camera_id} not found in {nfee_conf_dir}")


@exec_ui(display_name="Telemetry", use_kernel=True)
def telemetry(camera_id: Callback(camera_ids, name="Camera selection") = None, filename: FilePath = None,
              description: str = f"Telemetry dictionary for ...  (#...)"):
    """ Ingest the N-FEE sensor calibration in a new setup.

    In Sect. 1 (Create configuration / calibration files), we have already created a  YAML file with the N-FEE sensor
    calibration.  This information is now ingested in the setup and the setup is submitted (meaning that it is
    automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Full path of the telemetry dictionary file
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the telemetry dictionary has been ingested.
    """

    check_description(camera_id, description)
    check_filename(camera_id, filename.stem)

    tm_conf_dir = Path(os.environ["PLATO_CONF_REPO_LOCATION"]) / "data" / "common" / "telemetry"

    try:
        telemetry_dictionary = f"pandas//../../common/telemetry/{filename.relative_to(tm_conf_dir)}"

        print(f"About to set setup.camera.dictionary to {telemetry_dictionary}")
        response = input("Submit setup [Y/n] ? ")

        if response.lower() == 'y':
            setup = GlobalState.setup
            setup.telemetry.dictionary = telemetry_dictionary

            return submit_setup(setup, description)
        else:
            print("Changes not included in the setup")
    except ValueError:
        Abort(f"Telemetry dictionary for {camera_id} not found in {tm_conf_dir}")


# @exec_ui(display_name="Power consumption", use_kernel=True)
# def power_consumption(camera_id: Callback(camera_ids, name="Camera selection") = None,
#                       description: str = f"Power consumption checks for ...  (#...)"):
#     check_description(camera_id, description)


@exec_ui(display_name="Stages calibration", use_kernel=True)
def stages_calibration(camera_id: Callback(camera_ids, name="Camera selection") = None,
                       alpha_correction_coefficients: FixedList([float, float], [None, None],
                                                                name="(a,b) in a*θ + b") = None,
                       offset_delta_x: float = None,
                       delta_x_correction_coefficients: FixedList([float, float, float], [None, None, None],
                                                                  name="(a,b,c) in a*θ^2 + b*θ + c") = None,
                       phi_correction_coefficients: FixedList([float, float], [None, None],
                                                              name="(a,b) in a*θ + b") = None,
                       description: str = "Calibration of the Huber Stages for ..., "
                                          "as taken from vX.Y of PLATO-CSL-PL-RP-XXXX  (#...)"):
    """ Ingest the Huber Stages calibration information in a new setup.

    The calibration information of the Huber Stages is ingested in the setup and the setup is submitted (meaning that
    it is automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - alpha_correction_coefficients: Coefficients (a, b) in the equation for the mirror orientation in the CSL
                                         calibration report (Sect. "Definition of mirror orientation"), a*θ + b.  Note
                                         that the order will be reversed in the setup.
        - offset_delta_x: Zero in the equation for the mirror position in the CSL calibration report (Sect. "Definition
                          of the mirror position")
        - delta_x_correction_coefficients: Coefficients (a, b, c) in the polynomial for δ in the equation for the mirror
                                           position in the CSL calibration report (Sect. "Definition of the mirror
                                           position"), a*θ^2 + b*θ + c.  Note that the order will be reversed in the
                                           setup.
        - phi_correction_coefficients: Coefficients (a, b) in the polynomial for the φ correction in the equation for
                                       the mirror position in the CSL calibration report (Sect. "Definition of the
                                       mirror position"), a*θ + b.  Note that the order will be reversed in the setup.
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the Stages calibration information has been ingested.
    """

    check_description(camera_id, description)

    alpha_correction_coefficients.reverse()
    delta_x_correction_coefficients.reverse()
    phi_correction_coefficients.reverse()

    table = Table(title="Stages calibration")
    table.add_column("Parameter")
    table.add_column("Value")

    table.add_row("alpha_correction_coefficients (b, a)", str(alpha_correction_coefficients))
    table.add_row("offset_delta_x", str(offset_delta_x))
    table.add_row("delta_x_correction_coefficients (c, b, a)", str(delta_x_correction_coefficients))
    table.add_row("phi_correction_coefficients (b, a)", str(phi_correction_coefficients))

    console = Console(width=120)
    console.print(table)

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup

        setup.gse.stages.calibration.alpha_correction_coefficients = alpha_correction_coefficients
        setup.gse.stages.calibration.offset_delta_x = offset_delta_x
        setup.gse.stages.calibration.delta_x_correction_coefficients = delta_x_correction_coefficients
        setup.gse.stages.calibration.phi_correction_coefficients = phi_correction_coefficients

        return submit_setup(setup, description)

    else:
        print("Changes not included in the setup")


@exec_ui(display_name="Height collimated beam")
def height_collimated_beam(camera_id: Callback(camera_ids, name="Camera selection") = None, height: float = None,
                           description: str = "Set height of the collimated beam for ... (#...)"):
    """ Set the height of the collimated beam.

    The height of the collimated beam is ingested in the setup and the setup is submitted (meaning that
    it is automatically pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - height: Height of the collimated beam [mm].
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the Stages calibration information has been ingested.
    """
    check_description(camera_id, description)

    print(f"The height of the collimated beam will be set to {height}mm")

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup
        setup.gse.stages.calibration.height_collimated_beam = height
        return submit_setup(setup, description)

    else:
        print("Changes not included in the setup")


@exec_ui(display_name="Hexapod")
def set_hexapod_id(camera_id: Callback(camera_ids, name="Camera selection") = None,
                   hexapod_id: Callback(hexapod_ids, name="Hexapod") = None,
                   description: str = "Set hexapod ID for ... (#...)"):
    """ Set the hexapod identifier.

    The hexapod identifier is ingested in the setup and the setup is submitted (meaning that it is automatically
    pushed to the repository and loaded into the Configuration Manager).

    Args:
        - camera_id: Identifier for the camera (beer name)
        - hexapod_id: Hexapod identifier (for CSL1: 1A or 1B; for CSL2: 2A or 2B).
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)

    Returns: New setup in which the hexapod identifier has been ingested.
    """
    check_description(camera_id, description)

    print(f"The hexapod ID will be set to {hexapod_id}")

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':
        setup = GlobalState.setup
        setup.gse.hexapod.ID = hexapod_id
        return submit_setup(setup, description)
    else:
        print("Changes not included in the setup")


# @exec_ui(display_name="Isostatic plate")
# def set_isostatic_plate_id(camera_id: Callback(camera_ids, name="Camera selection") = None,
#                            isostatic_plate_id: Callback(isostatic_plate_identifiers, name="Isostatic plate") = None,
#                            description: str = "Set isostatic-plate ID for ... (#...)"):
#     """ Set the isostatic-plate identifier.
#
#     The isostatic-plate identifier is ingested in the setup and the setup is submitted (meaning that it is automatically
#     pushed to the repository and loaded into the Configuration Manager).
#
#     Args:
#         - camera_id: Identifier for the camera (beer name)
#         - isostatic_plate_id: Isostatic-plate identifier (1A, 1B, 2A, or 2B).
#         - description: Description for the new setup (incl. the camera name and the GitHub issue number)
#
#     Returns: New setup in which the isostatic-plate identifier has been ingested.
#     """
#     check_description(camera_id, description)
#
#     print(f"The isostatic-plate ID will be set to {isostatic_plate_id}")
#
#     response = input("Submit setup [Y/n] ? ")
#
#     if response.lower() == 'y':
#         setup = GlobalState.setup
#         setup.gse["isostatic_plate"] = {"ID": isostatic_plate_id}
#         return submit_setup(setup, description)
#     else:
#         print("Changes not included in the setup")


@exec_ui(display_name="CCD offsets and readout noise (SFT)", use_kernel=True)
def ccd_limits_sft(camera_id: Callback(camera_ids, name="Camera selection") = None,
                   ccd_offsets: FixedList([float, float], [None, None], name="offsets [ADU]") = [1000, 2000],
                   ccd_noise_limits: FixedList([float, float], [None, None], name="readout noise limits [ADU]") = [1., 3.],
                   description: str = "CCD limits for SFT ...  (#...)"):
    """ Ingest the CCD offsets and readout noise limits for the SFT.

    Args:
        - camera_id: Identifier for the camera (beer name)
        - ccd_offsets:
        - ccd_noise_limits:
        - description: Description for the new setup (incl. the camera name and the GitHub issue number)
    """

    check_description(camera_id, description)

    offsets = {}
    noise = {}

    for ccd_number in range(1, 5):
        for ccd_side in ["E", "F"]:
            offsets[f"{ccd_number}{ccd_side}"] = ccd_offsets
            noise[f"{ccd_number}{ccd_side}"] = ccd_noise_limits

    table = Table(title="CCD limits")
    table.add_column("Parameter")
    table.add_column("Value")

    table.add_row("offsets", str(offsets))
    table.add_row("noise", str(noise))

    console = Console(width=120)
    console.print(table)

    response = input("Submit setup [Y/n] ? ")

    if response.lower() == 'y':

        setup = GlobalState.setup

        limits = {"offsets": offsets, "noise": noise}
        setup.camera.ccd["limits"] = limits

        return submit_setup(setup, description)

    else:
        print("Changes not included in the setup")


def check_description(camera_id: str, description: str):
    """ Check whether the given camera ID is present in the given description.

    The idea is that the description will be used as description of a new setup (and will therefore appear in the
    history of the setups).  We want to enforce a proper description of the setup.

    Args:
        - camera_id: Identifier for the camera (beer name)
        - description: Description to use for a new setup

    Raises: Aborts if the given camera ID is not present in the given description.
    """

    if camera_id not in description:
        raise Abort(f"The camera name {camera_id} has not been included in the description of the new setup.  Fix this "
                    f"and run the task again.")


def check_filename(camera_id: str, filename: str):
    """ Check whether the given camera ID is present in the given filename.

    Args:
        - camera_id: Identifier for the camera (beer name)
        - filename: Filename

    Raises: Aborts if the given camera ID is not present in the given filename.
    """

    if camera_id not in filename:
        raise Abort(f"The camera name {camera_id} his not present in the filename {filename}.  Fix this and run the "
                    f"task again.")
