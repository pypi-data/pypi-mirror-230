from camtest.core.exec import building_block
# To be used only before KUL setup's the control manager
from demos.helper import load_test_setup
from egse.settings import Settings
from egse.state import GlobalState

load_test_setup()

THORLABS_SETTINGS = Settings.load("Thorlabs PM100 Controller")

################## TELEMETRY AND HK

@building_block
def get_value():

    """Returns Thorlabs PM100 measured power value"""

    print(f"reading power value in W")
    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_value()

@building_block
def get_average():

    """Returns Thorlabs PM100 correction wavelength in nm"""

    print("Reading of the number of samples that have been averaged")
    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_average()

@building_block
def get_wavelength():

    """Returns Thorlabs PM100 correction wavelength in nm"""

    print("Reading of correction wavelength in nm")
    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_wavelength()

@building_block
def get_diameter():

    """Returns Thorlabs PM100 correction beam diameter in mm"""

    print("Reading of correction beam diameter in mm")
    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_diameter()

@building_block
def get_range():

    """Gets Thorlabs power range in W and the autorange state. Returns a dictionary"""

    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_range()

@building_block
def get_autozero():

    """Gets Thorlabs autozero status and magnitude. Returns a dictionary"""

    thorlabs = GlobalState.setup.gse.thorlabs.device

    return thorlabs.get_autozero()

@building_block
def get_config():

    """Gets Thorlabs full parameters defined in the previous BB and set. Returns a dictionary"""
    thorlabs = GlobalState.setup.gse.thorlabs.device
    return thorlabs.get_config()

################### TELECOMMANDS

@building_block
def set_average(average = None):

    """sets the Thorlabs PM100 number of average samples"""
    thorlabs = GlobalState.setup.gse.thorlabs.device

    thorlabs.set_average(average = average)
    print("Average value set")
    return

@building_block
def set_wavelength(wave = None):

    """sets the Thorlabs PM100 correction wavelength in nm"""
    thorlabs = GlobalState.setup.gse.thorlabs.device

    thorlabs.set_wavelength(wave = wave)
    print("Wavelength set")
    return

@building_block
def set_range(range = None, auto = None):

    """sets the Thorlabs PM100 power range = up/down or in autorange. When autorange selected put range = None"""
    thorlabs = GlobalState.setup.gse.thorlabs.device

    thorlabs.set_range(range = range, auto = auto)
    print("range set")
    return

@building_block
def set_diameter(diameter = None):

    """sets the Thorlabs PM100 correction beam diameter in mm"""
    thorlabs = GlobalState.setup.gse.thorlabs.device

    thorlabs.set_diameter(diameter = diameter)
    print("beam diameter set")
    return

@building_block
def set_zero(autozero = None):

    """sets the Thorlabs PM100 autozero correction"""
    thorlabs = GlobalState.setup.gse.thorlabs.device

    thorlabs.set_zero(autozero = autozero)
    print("autozero correction done set")
    return