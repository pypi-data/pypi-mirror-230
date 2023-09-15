from camtest.core.exec import building_block
# To be used only before KUL setup's the control manager
from demos.helper import load_test_setup
from egse.settings import Settings
from egse.state import GlobalState

load_test_setup()

SHUTTER_SETTINGS = Settings.load("Shutter KSC101 Controller")

######## TELECOMMANDS

@building_block
def set_enable(status = None):

    """Enables the KSC101 Solenoid"""
    shutter = GlobalState.setup.gse.shutter.device

    shutter.set_enable(status = status)
    print("Set ")
    return

@building_block
def set_mode(mode = None):

    """sets the KSC101 Control mode to Manual/Single/Automatic/Trigger"""
    shutter = GlobalState.setup.gse.shutter.device

    shutter.set_mode(mode = mode)
    print("Mode set")
    return

@building_block
def set_cycle(on = None, off = None, number = None):

    """sets the KSC101 Control mode to Manual/Single/Automatic/Trigger"""
    shutter = GlobalState.setup.gse.shutter.device

    shutter.set_cycle(on = on, off = off, number = number)
    print("Cycle parameters set")
    return

##################### TELEMETRY

@building_block
def get_enable():

    """gets the KSC101 Controller enable state"""
    shutter = GlobalState.setup.gse.shutter.device

    enable = shutter.get_enable()

    print("the shutter is:", enable)

    return enable

@building_block
def get_mode():

    """gets the KSC101 Controller operating mode"""
    shutter = GlobalState.setup.gse.shutter.device

    mode = shutter.get_mode()
    modes = {1:"manual", 2: "single",3:"auto", 4:"trigger"}

    print("mode is:", mode, "(",modes[mode],")")

    return mode

@building_block
def get_cycle():

    """gets the KSC101 Controller cycling parameters"""
    shutter = GlobalState.setup.gse.shutter.device

    cycle = shutter.get_cycle()
    print(cycle)

    return cycle
