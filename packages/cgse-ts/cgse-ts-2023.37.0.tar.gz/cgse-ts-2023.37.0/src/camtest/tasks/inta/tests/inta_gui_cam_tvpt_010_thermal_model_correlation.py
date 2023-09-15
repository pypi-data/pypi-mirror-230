from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "5.- CAM-TVPT-010 Thermal Model Correlation"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="TVTT-PFM-01",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt010(
        num_subpix: int=25, 
        num_frames: int=2, 
        num_bck: int=2, 
        n_rows: int=None, 
        mode: str ="full", 
        dith_amp: float =0.012, 
        fwc_fraction: float = 0.0,
        fov_selection: list = [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39],
        fov_table: str ="reference_full_44_confirmed", 
        bandpass: int=None, 
        description: str="CAM-TVPT-010 best focus search at -75degC external sync"):

    """
    Runs the TVPT010 test described in PLATO CAM Test Plan
    Args:
        num_subpix: number of sub hexapod positions executed randomly at each FoV position (dithering)
        num_frames: number of images acquired at each sub-position
        num_bck: number of background images (shutter must be closed) acquired at the beginning of the series
        n_rows: number of rows of the appropriate CCD half to be actually read, speeds up the readout when the expected image is small
        mode: string, indicates if all CCDs should be read or only some of the 4
        dith_amp: max angular amplitude in degrees of each random sub-position of the dithering
        fwc_fraction: fraction of the pixel capacity to be filled by the incoming source intensity, regulated by the ND on the filter wheel
        fov_selection: list that allows to select a subset of the positions (theta, phi) listed in the setup file
        fov_table: provide the keyword name of the FoV table to be extracted from the setup file (e.g. 'reference_single', 'reference_full_40', 'reference_circle_20')        
        bandpass: allows to select the color filter to be used (None: white light, 1: Green, 2: Red, 3: NIR)
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """

    from camtest.commanding.cam_tvpt_010_best_focus_determination import cam_tvpt_010
    from camtest import execute

    execute(cam_tvpt_010, 
            num_subpix=num_subpix, 
            num_frames=num_frames, 
            num_bck=num_bck, 
            n_rows=n_rows, 
            mode=mode, 
            dith_amp=dith_amp, 
            fwc_fraction=fwc_fraction, 
            fov_table=fov_table, 
            fov_selection=fov_selection, 
            bandpass=bandpass,
            description=description)





    
    