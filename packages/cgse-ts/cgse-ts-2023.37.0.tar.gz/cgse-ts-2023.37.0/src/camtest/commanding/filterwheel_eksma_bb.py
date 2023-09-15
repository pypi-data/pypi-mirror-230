from camtest.core.exec import building_block
from egse.settings import Settings
from egse.state import GlobalState

FW_SETTINGS = Settings.load("Filter Wheel 8SMC4 Controller")

######## TELECOMMANDS

@building_block
def set_position(pos_wheel1 = None, pos_wheel2 = None):

    """sets the filterwheel to the positions given by the wheel 1 and the wheel 2.
    Each wheel position goes from 1 to 8"""

    filterwheel = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_position(pos_wheel1 = pos_wheel1, pos_wheel2 = pos_wheel2)

@building_block
def homing():
    """sets the filterwheel to the home position (0,0)"""
    filterwheel = GlobalState.setup.gse.filterwheel.device
    filterwheel.homing()

##################### TELEMETRY
@building_block
def get_position():

    """Gets the last set position of each of the filter wheels. Note this is not a real position but an echo
    of the last commanded position"""

    filterwheel = GlobalState.setup.gse.filterwheel.device

    """Returns a  list with [pos_wheel1, pos_wheel2]"""
    position = filterwheel.get_position()

    return position

def att_get_level():

    """Reports current attenuator level (a factor 0..1) and its corresponding wheel position."""

    filterwheel = GlobalState.setup.gse.filterwheel.device

    """Returns a  list with [wheel one index position, wheel 2 index position, attenuator factor]"""
    level = filterwheel.att_get_factor()

    return level

@building_block
def get_status():

    """Gets the status of the filterwheel motor controller
    Returns a list with [Current position, Speed, Temperature, Current, Voltage, statusFlags]"""
    filterwheel = GlobalState.setup.gse.filterwheel.device

    _status = filterwheel.get_status()

    return _status

@building_block
def att_status():

    """Reports if device attenuator is ready for use.
    Returns a dictionary with all the status flags coming from get_status command"""
    filterwheel = GlobalState.setup.gse.filterwheel.device

    _status = filterwheel.att_status()

    return _status



