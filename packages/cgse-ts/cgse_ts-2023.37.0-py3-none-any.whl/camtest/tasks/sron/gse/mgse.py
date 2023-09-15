from pathlib import Path
import numpy as np

from egse.state import GlobalState

from camtest import end_observation, start_observation
from camtest.commanding import mgse
from camtest import execute

from gui_executor.exec import exec_ui

UI_MODULE_DISPLAY_NAME = "Facility Gimbal"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Enable Gimbal",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def enable_gimbal():
    print("Enabling gimbal")
    execute(mgse.enable, description="Enable Gimbal")

@exec_ui(display_name="Disable Gimbal",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def disable_gimbal():
    print("Disbling gimbal")
    execute(mgse.disable, description="Disable Gimbal")

@exec_ui(display_name="Home Gimbal",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def home_gimbal():
    
    start_observation("Home Gimbal")
    print('Homing gimbal')
    try:
        with GlobalState.setup.gse.ensemble.device as gimbal:
            gimbal.home_axes()
    except ConnectionError as exc:
        print(f"Could not home the Gimbal: {exc}")
            
    end_observation()

@exec_ui(display_name="Zero Gimbal",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def zero_gimbal():
    
    start_observation("Move Gimbal to Zero position")
    
    try:
        with GlobalState.setup.gse.ensemble.device as gimbal:
            gimbal.move_axes_degrees(0, 0)
    except:
        print(f"Could not zero the gimbal")
    
    end_observation()

@exec_ui(display_name="Move Gimbal degrees",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def move_gimbal_degrees(x: float = np.arange(-20, 20, 0.001),
                        y: float = np.arange(-20, 20, 0.001)):
    
    start_observation(f"Move Gimbal to X: {x}, Y:{y}")
    
    try:
        with GlobalState.setup.gse.ensemble.device as gimbal:
            gimbal.move_axes_degrees(x, y)
    except:
        print(f"[red]Could not move the gimbal")
    
    end_observation()

@exec_ui(display_name="Move Gimbal FoV",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def move_gimbal_fov(theta: float = np.arange(0, 20, 0.001),
                    phi: float = np.arange(-180, 180, 0.001), 
                    wait: bool = [True, False]):
    execute(mgse.point_source_to_fov, 
            theta=theta, 
            phi=phi, 
            wait=wait, 
            description=f"Moving gimbal to FoV theta: {theta:.2f}, phi: {phi:.2f}")

@exec_ui(display_name="Move Gimbal FP",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def move_gimbal_fp(x, y, wait):
    execute(mgse.point_source_to_fp, 
            x=x, 
            y=y, 
            wait=wait, 
            description=f"Moving gimbal to FP x: {x:.2f}, y: {y:.2f}")
    
