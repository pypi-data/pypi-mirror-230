# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 10:52:44 2022

@author: pierre
"""

from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List, Callback
from pathlib import Path

from gui_executor.exec import exec_ui, Directory
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "2 — TVPT010 — EEF ext sync"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


def fov_positions_table() -> List:
    """ Returns list of valid field of view positions names for the TVPT010.

    This list is composed of the information in the setup (fov_positions).

    Returns: List of allowed table names.
    """

    fov_positions_list = list(GlobalState.setup.fov_positions.keys())

    default_fov_positions = "reference_full_40"
    if default_fov_positions in fov_positions_list:
        fov_positions_list.insert(0, fov_positions_list.pop(fov_positions_list.index("reference_full_40")))

    return fov_positions_list


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_ext_psf(
        num_subpix: int = 25,
        num_frames: int = 2,
        num_bck: int = 2,
        n_rows: int = 500,
        mode: Callback(lambda: ["partial", "full"], name="CCD readout mode") = None,
        dith_amp: float = 0.012,
        fwc_fraction: float = 1.6,
        fov_table: Callback(fov_positions_table, name="Fov positions names") = None,
        fov_selection: list = None,
        bandpass: Callback(lambda: [None, 1, 2, 3], name="Bandpass colors") = None,
        description: str = 'TVPT010 PSF at optimal temperature ext sync (prev. TVPT031)',
):
    """
    Runs the TVPT031 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        mode: string, indicates if all CCDs should be read or only some of the 4
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_table: provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        bandpass: allows to select the color filter to be used (None: white light, 1: Green, 2: Red, 3: NIR)
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_010_best_focus_determination import cam_tvpt_010
    from camtest import execute

    execute(cam_tvpt_010, num_subpix=num_subpix, num_frames=num_frames, num_bck=num_bck, n_rows=n_rows, mode=mode,
            dith_amp=dith_amp, fwc_fraction=fwc_fraction, fov_table=fov_table, fov_selection=fov_selection,
            bandpass=bandpass, description=description)
