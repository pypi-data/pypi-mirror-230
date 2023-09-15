import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from enum import IntEnum
from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "LakeShore 336"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

class Output(IntEnum):
    Output_Loop_1  = 1
    Output_Loop_2  = 2

class Range(IntEnum):
    Off     = 0
    Low     = 1
    Medium  = 2
    High    = 3

class AtuneMode(IntEnum):
    P   = 0
    PI  = 1
    PID = 2

class LakeShoreIndex(IntEnum):
    LSCI_1  = 1
    LSCI_2  = 2
    LSCI_3  = 3

class HeaterResistant(IntEnum):
    R_25 = 1
    R_50 = 2

class MaxCurrentMode(IntEnum):
    User_Specified  = 0
    A_0_707         = 1
    A_1             = 2
    A_1_141         = 3
    A_2             = 4

class OutputDisplay(IntEnum):
    Current = 1
    Power   = 2

@exec_ui(display_name="Set Automatic PID", use_kernel=True,
         icons=(ICON_PATH / "lakeshore-pid.svg", ICON_PATH / "lakeshore-pid-selected.svg"))
def set_pid_automatic(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1, autotune_mode: AtuneMode = AtuneMode.PID, description: str = 'Change Automatic PID on the LakeShore 336'):
    """
    This function put the PID in mode AutoTune in LakeShore 336.
    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
        - autotune_mode: Mode in which to set LakeShore AutoTune(P/PI/PID)
        - description: Command description for the observation
    """
    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
    start_observation(description)
    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            lakeshore.set_autotune(output=output.value, mode=autotune_mode.value) 
            time.sleep(1.0)
            tuning = lakeshore.get_tuning_status()    
            print(f"[green]LakeShore Tunning is this values: {tuning}.[/]", flush=True)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Set Setpoint", use_kernel=True,
         icons=(ICON_PATH / "lakeshore-setpoint.svg", ICON_PATH / "lakeshore-setpoint-selected.svg"))
def set_setpoint(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1 ,value: str = 20,description: str = 'Change Set Point on the LakeShore 336'):
    """
    This function changed the Set Point in LakeShore 336.
    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
        - value: Set point value to command
        - description: Command description for the observation
    """
    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
    start_observation(description)
    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            lakeshore.set_setpoint(output=output.value, value=value) 
            time.sleep(1.0)
            setpoint = lakeshore.get_setpoint(output.value)    
            print(f"[green]LakeShore Setpoint is: {setpoint}.[/]", flush=True)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Set PID Manual", use_kernel=True,
         icons=(ICON_PATH / "lakeshore-pid-manual.svg", ICON_PATH / "lakeshore-pid-manual-selected.svg"))
def set_pid_manual(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1, p_value: int = 1,i_value: int = 1,d_value: int = 1,description: str = 'Change Manual PID on the LakeShore 336'):
    """
    This function changed the PID Values LakeShore 336.
    
    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
        - p_value: P value in PID Manual
        - i_value: I value in PID Manual
        - d_value: D value in PID Manual
        - description: Command description for the observation
    """
    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
    start_observation(description)
    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            lakeshore.set_params_pid(output=output.value, p=p_value,i=i_value,d=d_value) 
            time.sleep(1.0)
            pid = lakeshore.get_params_pid(output.value)    
            print(f"[green]LakeShore PID is this values: {pid}.[/]", flush=True)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Set Heater Setup", use_kernel=True,
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def set_heater_setup(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1, heater_resistance: HeaterResistant = HeaterResistant.R_25, max_current_mode: MaxCurrentMode = MaxCurrentMode.User_Specified, max_current_user: str = "0.32",output_display: OutputDisplay = OutputDisplay.Current,description: str = 'Change Heater Setup on the LakeShore 336'):
    """
    This function changed the Heater Setup LakeShore 336.
    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
        - heater_resistance: Resistance of heater (25 Ohms or 50 Ohms)
        - max_current_mode: Max current mode the heater (User_Specified / A_0_707 = 0,707A / A_1 = 1A / A_1_141 = 1,141A / A_2 = 2 A)
        - max_current_user: if in max_current_mode select User_Specified, it's necesary set the value here.
        - output_display: Select values display (Current/Power)
        - description: Command description for the observation
    """
    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
    start_observation(description)
    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            lakeshore.set_heater_setup(output=output.value,heater_resistance=heater_resistance.value, max_current=max_current_mode.value, max_user_current=max_current_user, output_display=output_display.value) 
            time.sleep(1.0)
            heater = lakeshore.get_heater_status(output.value)    
            print(f"[green]LakeShore Heater is this values: {heater}.[/]", flush=True)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Set Range", use_kernel=True,
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def set_range(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1, heater_range: Range = Range.Off, description: str = 'Set Range on the LakeShore 336'):
    """
    This function changed the Range in LakeShore 336.

    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
        - heater_range: Selects the heating ramp level (Off/Low/Medium/High).
        - description: Command description for the observation
    """

    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy
    start_observation(description)
    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            lakeshore.set_range(output=output.value,range=heater_range.value) 
            time.sleep(1.0)
            range = lakeshore.get_range(output.value)    
            print(f"[green]LakeShore Range is this values: {range}.[/]", flush=True)
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")

    end_observation()

@exec_ui(display_name="Status", use_kernel=True)
def print_status_lakeshore(lsci_index: LakeShoreIndex = LakeShoreIndex.LSCI_1, output: Output = Output.Output_Loop_1):
    """This function prints a table with the status of the Lakeshore 336.
    
    Args:
        - lsci_index: LakeShore index to command (LSCI_1/LSCI_2/LSCI_3)
        - output: Output of the LakeShore where to perform (Output_Loop_1/Output_Loop_2)
    """
    from rich.console import Console
    from rich.table import Table
    from egse.tempcontrol.lakeshore.lsci import LakeShoreProxy

    try:
        with LakeShoreProxy(lsci_index.value) as lakeshore:
            table           =   Table(title=f"LakeShore {lsci_index.value} Status Report")            
            temperature     =   lakeshore.get_temperature()
            pid_params      =   lakeshore.get_params_pid(output.value)                
            setpoint        =   lakeshore.get_setpoint(output.value)
            range           =   lakeshore.get_range(output.value)
            heater_status    =   lakeshore.get_heater_status(output.value)
            heater_setup     =   lakeshore.get_heater_setup(output.value)
            tunning_status   =   lakeshore.get_tuning_status()
            heater_output    =   lakeshore.get_heater(output.value)

            table.add_row("Temperature"             ,   str(temperature))
            table.add_row("Heater Output"           ,   str(heater_output))
            table.add_row("Setpoint"                ,   str(setpoint))
            table.add_row("Range"                   ,   str(range))
            if len(pid_params) > 2:
                table.add_row("Param P"                 ,   str(pid_params[0]))
                table.add_row("Param I"                 ,   str(pid_params[1]))
                table.add_row("Param D"                 ,   str(pid_params[2]))
            else:
                table.add_row("Param PID"                 ,   str(f"Error: {pid_params}"))
            table.add_row("Heater Status"           ,   str(heater_status))
            if len(heater_setup) > 3:
                table.add_row("Heater Resistance"       ,   str(heater_setup[0]))
                table.add_row("Heater Max Current"      ,   str(heater_setup[1]))
                table.add_row("Heater Max User Current" ,   str(heater_setup[2]))
                table.add_row("Heater Display"          ,   str(heater_setup[3]))
            else:
                table.add_row("Heater Setup"                 ,   str(f"Error: {heater_setup}"))    
            if len(tunning_status) > 3:
                table.add_row("Tunning Status"          ,   str(tunning_status[0]))
                table.add_row("Tunning Output"          ,   str(tunning_status[1]))
                table.add_row("Tunning Error Status"    ,   str(tunning_status[2]))
                table.add_row("Tunning Stage Status"    ,   str(tunning_status[3]))
            else:
                table.add_row("Tunning Status"          ,   str(f"Error: {tunning_status}"))

            console = Console(width=80)
            print(lakeshore.info())
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the LakeShore Server, check in the PM GUI if it's running.[/]")
