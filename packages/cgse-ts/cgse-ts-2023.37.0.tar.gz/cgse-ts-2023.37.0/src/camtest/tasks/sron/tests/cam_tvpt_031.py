# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 10:52:44 2022

@author: pierre
"""


from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "6 — TVPT031 — full PSF ext sync"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="CAM-TVPT-031",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt031_psf(
        num_subpix: int = 25,
        num_frames: int = 2,
        num_bck: int = 2,
        n_rows: int = None,
        dith_amp: float = 0.012,
        fwc_fraction: float = 8.51e-5,
        fov_selection: list = [11,12,13,14,15,16,17,18,19,20],
        mode: str = "full",
        fov: str = 'full',
        description: str = 'TVPT031 PSF at optimal temperature ext sync',
):
    """
    Runs the TVPT031 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        fov: name of the (theta, phi) positions to be used in the setup file
        mode: string, indicates if all CCDs should be read or only some of the 4
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """
    from camtest.commanding.cam_tvpt_010_best_focus_determination import cam_tvpt_010
    from camtest import execute

    execute(cam_tvpt_010, num_subpix=num_subpix, num_frames=num_frames, num_bck=num_bck,
            n_rows=n_rows, dith_amp=dith_amp, mode=mode,
            fwc_fraction=fwc_fraction, fov_selection=fov_selection,
            fov=fov, description=description)
