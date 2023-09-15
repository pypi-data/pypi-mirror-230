from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "8.- CAM-TVPT-080  Dynamic Range"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="dataset#80-2",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_tvpt080_2(
        mag_list: list = [1, 4, 6, 7, 8, 9, 11, 16], 
        num_frames: int = 5, 
        num_subpix: int = 5, 
        num_bck: int = 3, 
        exposure_time: float = 0.1, 
        fov_list: list = [[4,45], [14,45]], 
        description: str="TP#16 Dynamic Range_reduced version - CAM-TVPT-80"):

    """
    Runs the TVPT080 int sync test described in PLATO CAM Test Plan
    Args:
        mag_list: list of stellar magnitudes to be imitated by the source and attenuators
        num_frames: number of images
        num_subpix: number of sub-positions to be acquired for dithering
        num_bck: number of background images to be acquired at beginning of each position
        exposure_time: integration time in s of each frame
        fov_list: list of [theta, phi] positions in the focal plane
        description: text that will be saved along with the OBSID to identify it, should contain the test plan item identifier (such as TVPT-XXX)
    """

    from camtest.commanding.cam_tvpt_080_dynamic_range_int_sync  import cam_tvpt_080_int_sync
    from camtest import execute

    import numpy as np
    fov_array = np.array(fov_list)
    
    execute(cam_tvpt_080_int_sync, 
            mag_list = mag_list, 
            num_frames = num_frames, 
            num_subpix = num_subpix, 
            num_bck = num_bck, 
            exposure_time = exposure_time, 
            fov_list = fov_list, 
            description = description)
    



    
    
