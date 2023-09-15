import csv
import datetime

import numpy as np

from pathlib import Path

from egse.state                             import GlobalState
from egse.hk                                import get_housekeeping
from egse.system                            import EPOCH_1958_1970

from camtest import execute
from camtest import building_block
from gui_executor.exec import exec_ui

UI_MODULE_DISPLAY_NAME = "10 — Facility Vacuum"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Valves Check control",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def valve_check():
    execute(sron_facility_valve_check,
            description="Verify all facility valves")
        
    
@building_block
def sron_facility_valve_check(full=False):
    valves = GlobalState.setup.gse.beaglebone_vacuum.device
    
    # Go through every valve and confirm the right ones are opening
    # Set full argument to True to test the gate and vent valve as well
    
    valve_codes      = ['MV011', 'MV012', 'MV013', 'MV014', 'MV021', 'MV022', 'MV023', 'MV024']
    valve_names = ['LN2 Shroud', 'LN2 TEB-FEE', 'LN2 TEB-TOU', 'LN2 TRAP', 'N2 Shroud', 'N2 TEB-FEE', 'N2 TEB-TOU', 'N2 Trap']

    if full:
        valve_codes.append(['MV002', 'MV001'])
        valve_names.append(['Gate valve', 'Vent valve'])
    
    correct = {}

    for valve, name in zip(valve_codes, valve_names):
        print('Opening the {} valve'.format(name))
        valves.set_valve(valve, True)
        if input("Is the {} valve open? (y/n)").lower().startswith('y'):
            correct[name] = True
        else:
            correct[name] = False
            print(f"{name} has been connected incorrectly")
        valves.set_valve(valve, False)