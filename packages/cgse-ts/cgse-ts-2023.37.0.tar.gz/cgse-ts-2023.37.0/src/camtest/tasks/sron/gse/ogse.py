from pathlib import Path

from egse.state import GlobalState

from camtest.commanding import ogse
from camtest import start_observation, end_observation
from camtest import execute

from gui_executor.exec import exec_ui


UI_MODULE_DISPLAY_NAME = "Facility OGSE"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

@exec_ui(display_name="Turn OGSE on",
         icons=(ICON_PATH / "ogse-swon.svg", ICON_PATH / "ogse-swon-selected.svg"))
def turn_on_ogse():
    execute(ogse.ogse_swon, description="Turning on the OGSE")

@exec_ui(display_name="Turn OGSE off",
         icons=(ICON_PATH / "ogse-swoff.svg", ICON_PATH / "ogse-swoff-selected.svg"))
def turn_off_ogse():
    execute(ogse.ogse_swoff, description="Turning off the OGSE")

@exec_ui(display_name="Turn on lamp",
         icons=(ICON_PATH / "lamp.svg", ICON_PATH / "lamp-selected.svg"))
def turn_on_lamp():
    print("Turning on EQ99 LDLS")
    execute(ogse.sron_ldls_power_on, description="Turn on EQ99 Lamp")
        
@exec_ui(display_name="Turn off lamp",
         icons=(ICON_PATH / "lamp.svg", ICON_PATH / "lamp-selected.svg"))
def turn_off_lamp():
    print("Turning off EQ99 LDLS")
    execute(ogse.sron_ldls_power_off, description="Turn on EQ99 Lamp")

@exec_ui(display_name="Fix lamp controller fault",
         icons=(ICON_PATH / "lamp.svg", ICON_PATH / "lamp-selected.svg"))
def fix_lamp_fault():

    start_observation("Resolving lamp controller fault")

    print("Resolving EQ99 lamp controller fault...")

    with GlobalState.setup.gse.beaglebone_lamp.device as lamp:
        lamp.fix_controller_fault()
        
    end_observation()

@exec_ui(display_name="Open shutter",
         icons=(ICON_PATH / "shutter.svg", ICON_PATH / "shutter-selected.svg"))
def open_shutter():

    print("Opening SC10 shutter")
    
    execute(ogse.shutter_open, description="Open SC10 Shutter")

@exec_ui(display_name="Close shutter",
         icons=(ICON_PATH / "shutter.svg", ICON_PATH / "shutter-selected.svg"))
def close_shutter():
    
    print("Closing SC10 shutter")
    
    execute(ogse.shutter_close, description="Close SC10 Shutter")

@exec_ui(display_name="Home filterwheel",
         icons=(ICON_PATH / "filter-wheel-homing.svg", ICON_PATH / "filter-wheel-homing-selected.svg"))
def home_filterwheel():
    
    print("Homing filterwheel")
    
    with GlobalState.setup.gse.filterwheel.device as filterwheel:
        filterwheel.home()
        
@exec_ui(display_name="Zero filterwheel",
         icons=(ICON_PATH / "filter-wheel.svg", ICON_PATH / "filter-wheel-selected.svg"))
def zero_filterwheel():
    
    print("Bringing filterwheel to Zero position")
    
    start_observation("Move filterwheel to zero position")
    
    with GlobalState.setup.gse.filterwheel.device as filterwheel:
        filterwheel.set_position_wheels(0, 0)

@exec_ui(display_name="Move filterwheel",
         icons=(ICON_PATH / "filter-wheel-move.svg", ICON_PATH / "filter-wheel-move-selected.svg"))

def move_filterwheel(wheel0: int=range(8),
                     wheel1: int=range(8)):
    
    print(f"Moving filterwheel to wheel {wheel0} and {wheel1}")
    
    with GlobalState.setup.gse.filterwheel.device as filterwheel:
        filterwheel.set_position_wheels(wheel0, wheel1)

@exec_ui(display_name="Set filterwheel intensity",
         icons=(ICON_PATH / "filter-wheel-move.svg", ICON_PATH / "filter-wheel-move-selected.svg"))
def set_intensity(intensity):
    
    print(f"Setting filterwheel intensity to: {intensity}")
    
    with GlobalState.setup.gse.filterwheel.device as filterwheel:
        filterwheel.set_re

@exec_ui(display_name="Home hartmann mask",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def home_hartmann():
    
    print(f"Homing hartmann mask stage")
    
    start_observation("Home hartmann mask stage")
    
    with GlobalState.setup.gse.smd3.device as hartmann:
        hartmann.run_homing()
        
    end_observation()

@exec_ui(display_name="Move hartmann mask",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def move_hartmann(position: int=range(40000)):
    
    print(f"Moving hartmann mask stage to: {position} steps")
    
    start_observation(f"Move hartmann move to: {position}")
    
    with GlobalState.setup.gse.smd3.device as hartmann:
        hartmann.absolute_move(position)
        
    end_observation()

@exec_ui(display_name="Move mask into FoV",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def hartmann_in_fov():
    
    print("Move Hartmann mask into FoV")
    
    execute(ogse.hartmann_select, description="Move hartmann mask in FoV")

@exec_ui(display_name="Move mask out of FoV",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def hartmann_out_fov():
    
    print("Move Hartmann mask out of FoV")
    
    execute(ogse.hartmann_deselect, description="Move hartmann mask out of FoV")

@exec_ui(display_name="Stop hartmann mask",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def stop_hartmann():
    
    start_observation("Emergency stop Hartmann")
    
    print("Stop hartmann mask stage")
    
    with GlobalState.setup.gse.smd3.device as hartmann:
        hartmann.emergency_stop()
        
    end_observation()
    
@exec_ui(display_name="Get current power",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def get_power():
    
    start_observation("Fetch Powermeter power")
    
    with GlobalState.setup.gse.powermeter.device as powermeter:
        power = powermeter.get_value()
        
    print(f"Current power: {power} W")
    
    end_observation()
