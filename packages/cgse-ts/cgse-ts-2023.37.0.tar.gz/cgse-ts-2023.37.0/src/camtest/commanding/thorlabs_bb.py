from camtest.core.exec import building_block
from egse.settings import Settings
from egse.state import GlobalState

THORLABS_SETTINGS = Settings.load("Thorlabs PM100 Controller")

@building_block
def get_value():

    print(f"The value should be printed")
    thorlabs = GlobalState.setup.gse.thorlabs

    return thorlabs.device.get_value()
