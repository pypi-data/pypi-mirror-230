from camtest.core.exec import building_block
from egse.settings import Settings
from egse.state import GlobalState

FW_SETTINGS = Settings.load("Lamp EQ99 Controller")

######## TELECOMMANDS
@building_block
def set_enable(_enable = None):

    """sets the lamp EQ99 ON"""

    lamp = GlobalState.setup.gse.lamp.device
    lamp.set_enable(_enable = _enable)

##################### TELEMETRY
@building_block
def get_enable():

    """gets the lamp EQ99 status"""

    lamp = GlobalState.setup.gse.lamp.device

    """Returns a bool corresponding to the ON/OFF status of the lamp"""

    _status = lamp.get_enable()

    return _status