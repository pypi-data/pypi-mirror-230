# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 16:55:15 2022

@author: pierre
"""


from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "1 — TVPT010_internal_colors"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Command",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010_int_colors(
        num_subpix: int = 25,
        num_frames: int = 4,
        num_bck: int = 2,
        n_rows: int = 100,
        exposure_time: float = 3.0,
        clearout: bool = True,
        dith_amp: float = 0.012,
        fwc_fraction: float = 81.0,
        fov_selection: list = None,
        bandpass: int = 0,
        fov_table: str = 'reference_full_40',
        description: str = 'TVPT010 EEF across FoV in color filters',
):
    """
    Runs the TVPT010 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        exposure_time: integration time of each sub-position in seconds
        clearout: reset of the CCD between each image, should be true to diminish persistence risks
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        bandpass: if 0 or None, normal behaviour with both wheels used to obtain the requested fwc_fraction. If 1,2,3 selects green, red, NIR colors and thus reduces the range of available attenuations
        fov_table: name of the (theta, phi) positions to be used in the setup file
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_010_best_focus_determination_int_sync import cam_tvpt_010_int_sync
    from camtest import execute

    execute(cam_tvpt_010_int_sync, num_subpix=num_subpix, num_frames=num_frames, num_bck=num_bck,
            n_rows=n_rows, exposure_time=exposure_time, clearout=clearout, dith_amp=dith_amp,
            fwc_fraction=fwc_fraction, fov_selection=fov_selection,
            bandpass=bandpass, fov_table=fov_table, description=description)

