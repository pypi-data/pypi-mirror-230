from pathlib import Path
from time                                   import time, sleep
from rich.console import Console
from rich.table import Table

from egse.state                             import GlobalState
from egse.hk                                import get_housekeeping
from egse.system                            import EPOCH_1958_1970

from camtest import execute
from camtest import building_block

from gui_executor.exec import exec_ui

UI_MODULE_DISPLAY_NAME = "9 — Facility TGSE"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

PREFIXES = ["GSRON_AG34972_0_T", "GSRON_AG34972_1_T", "GSRON_AG34970_0_T", "GSRON_AG34970_1_T"]

@exec_ui(display_name="TGSE Find PT1000s",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def tgse_sensor_check():
    """ Validate the readout of all temperature sensors in the facility
    
    The test script does the following for all temperature sensors:
    1. Read latest value from housekeeping
    2. Make sure the value is not older than 30 seconds
    3. Make sure the value readout is realistic: 45 - -180
    
    After iterating over all available sensors it will print tables indicating the
    status of all temperature sensors
    """
    execute(sron_tgse_sensor_check,
            description="Validating all facility temperature sensors")

@exec_ui(display_name="TGSE Find PT1000 Heater pairs",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def tgse_sensor_heater_check():
    
    execute(sron_tgse_sensor_heater_check,
            description="Validating all facility temperature sensor and heater pairs")

@exec_ui(display_name="TGSE Check PID control loops",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def tgse_pid_check():
    
    execute(sron_tgse_pid_check,
            description="Validating all facility PID control loop")

class pt1000_heater:
    def __init__(self, htr_idx, htr_chnl, daq, daq_chnl):
        self.htr_idx    = htr_idx
        self.htr_chnl   = htr_chnl
        self.daq        = daq
        self.daq_chnl   = daq_chnl
        self.correct    = False
   
def housekeeping_age_too_old(timestamp, max_age=60):
    """ Returns True when housekeeping value is too old """
    if time() - (timestamp - EPOCH_1958_1970) > max_age:
        return True
    
def housekeeping_out_of_valid_range(value, range=[0, 45]):
    """ Returns True when housekeeping is out of range """
    if range[0] <= value <= range[1]:
        return False
    
    return True

@building_block
def sron_tgse_sensor_check():
    setup       = GlobalState.load_setup()
    console     = Console()
    
    setup_0_1   = setup.gse.agilent34970_1
    channels = setup_0_1.two_wire + setup_0_1.four_wire + setup_0_1.thermocouples
    
    table   = Table("Agilent 34970A 1 Temperature sensors")
    table.add_column("Status")
    for channel in channels:
        try:
            timestamp, value = get_housekeeping(PREFIXES[3] + f"{channel}")
            value = float(value)
            
            if housekeeping_age_too_old(timestamp):
                table.add_row(str(channel), 'Too old', style='#FF0000')
                continue
            
            if housekeeping_out_of_valid_range(value):
                table.add_row(str(channel), f'Over/Under range: {value:.2f}', style='#FF0000')
                continue
            
            table.add_row(str(channel), f'Correct: {value:.2f}', style='#008000')
        except:
            table.add_row(str(channel), f'Missing', style='#FF0000')       
    
    console.print(table)
    
    setup_2_0 = setup.gse.agilent34972_0
    channels = setup_2_0.two_wire + setup_2_0.four_wire + setup_2_0.thermocouples
    
    table = Table("Agilent 34972A 0 Temperature sensors")
    table.add_column("Status")

    for channel in channels:
        try:
            timestamp, value = get_housekeeping(PREFIXES[0] + f"{channel}")
            value = float(value)
            
            if housekeeping_age_too_old(timestamp):
                table.add_row(str(channel), 'Too old', style="#FF0000")
                continue
            
            if housekeeping_out_of_valid_range(value):
                table.add_row(str(channel), f'Over/Under range: {value:.2f}', style="#FF0000")
                continue
            
            table.add_row(str(channel), f'Correct: {value:.2f}', style='#008000')
        except:
            table.add_row(str(channel), f'Missing', style='#FF0000')
            
    
    console.print(table)
    
    setup_2_1 = setup.gse.agilent34972_1
    channels = setup_2_1.two_wire + setup_2_1.four_wire + setup_2_1.thermocouples
    
    table = Table("Agilent 34972A 1 Temperature sensors")
    table.add_column("Status")

    for channel in channels:
        try:
            timestamp, value = get_housekeeping(PREFIXES[1] + f"{channel}")
            value = float(value)
            
            if housekeeping_age_too_old(timestamp):
                table.add_row(str(channel), 'Too old', style="#FF0000")
                continue
            
            if housekeeping_out_of_valid_range(value):
                table.add_row(str(channel), f'Over/Under range: {value:.2f}', style="#FF0000")
                continue
            
            table.add_row(str(channel), f'Correct: {value:.2f}', style='#008000')
        except:
            table.add_row(str(channel), f'Missing', style='#FF0000')
            
    
    console.print(table)

@building_block
def sron_tgse_sensor_heater_check():
    try:
        heaters = GlobalState.setup.gse.beaglebone_heater.device
    except:
        raise Exception("Could not connect to proxy")
    
    def roc_housekeeping(daq, daq_chnl):
        try:
            timestamp, values = get_housekeeping(hk_name=PREFIXES[daq] + f"{daq_chnl}", time_window=30)
        except Exception as ex:
            print(f"Could not find HK: {ex}")
            raise ex
        
        deltaY = float(values[-1]) - float(values[0])
        deltaX = float(timestamp[-1]) - float(timestamp[0])
        roc    = deltaY / deltaX

        if time() - (float(timestamp[-1]) - EPOCH_1958_1970) > 60:
            raise Exception("Data too old")

        return float(roc)
    
    # Retrieve heater configuration from setup
    setup = GlobalState.load_setup()
    heater_config = setup.gse.spid.configuration.heaters
    
    pt1000_heater_list = []
    
    # Generate a list of all pairs based with heaters in ascending order
    for name, configurations in heater_config.items():
        
        for config in configurations:
            pt1000_heater_list.append(pt1000_heater(config[3], config[4], config[1], config[2]))

    pt1000_heater_list.sort(key=lambda x: x.htr_idx)

    
    print("Starting evaluation loop....")
    for pair in pt1000_heater_list:
        try:
            correct = True
            print(f"Turning on Heater {pair.htr_idx + 1} {chr(65+pair.htr_chnl)}")
            heaters.set_duty_cycle(pair.htr_idx, pair.htr_chnl, 5000)
            heaters.set_enable(pair.htr_idx, pair.htr_chnl, True)
            
            start_time = time()
            
            print(f"Current RoC: {roc_housekeeping(pair.daq, pair.daq_chnl)}")
            
            print(f"Waiting for a change on: {PREFIXES[pair.daq]}{pair.daq_chnl}")
            
            while not roc_housekeeping(pair.daq, pair.daq_chnl) > 0.0001:
                print(f"Current RoC: {roc_housekeeping(pair.daq, pair.daq_chnl)}, time left: {60 - (time() - start_time)}", end='\r')
                if time() - start_time > 60:
                    print("No change detected on {PREFIXES[pair.daq]}{pair.daq_chnl}")
                    correct = False
                    break
                sleep(1)
            
            print(f"Heater pair is {correct}")
            
            pair.correct = correct

        except Exception as ex:
            print(f"Skipped PID channel : {ex}")
        finally:
            print(f"Turning off Heater {pair.htr_idx + 1} {chr(65+pair.htr_chnl)}")
            heaters.set_enable(pair.htr_idx, pair.htr_chnl, False)
    
    for pair in pt1000_heater_list:
        print(f"Heater {pair.htr_idx + 1} {chr(65+pair.htr_chnl)}, {PREFIXES[pair.daq]}{pair.daq_chnl} {pair.correct}")

@building_block        
def sron_tgse_pid_check():
    
    pid = GlobalState.setup.gse.spid.device
    
    setup    = GlobalState.load_setup()
    heaters  = setup.gse.spid.configuration.heaters
    
    pid_list = {}
    
    for name, configurations in heaters.items():
        pid_list[name] = []
        for config in configurations:
            pid_list[name].append(config)
    
    correct = {}

    # Turn on PID to 25C
    for name, config in pid_list.items():
        for parameter in config:
            pid.set_temperature(parameter[0], 25)
            pid.enable(True)
            start_time = time()
        
            print(f"Turning on heater {parameter[3]} channel {parameter[4]} to test PID loop {parameter[0]} on PT1000 {PREFIXES[parameter[1]]}{parameter[2]}")
            
            while True:
                timestamp, value = get_housekeeping(f"{PREFIXES[parameter[1]]}{parameter[2]}")
            
                if float(value) >= 24.9:
                    print(f"PID channel {parameter[0]}: Correct")
                    correct[parameter[0]] = True
                    break
                elif (time() - start_time) > 300:
                    print(f"PID channel {parameter[0]}: Timeout, check if correct")
                    correct[parameter[0]] = False
                    break
                
                sleep(10)
                    
            print(f"Turning off heater {parameter[3]} channel {parameter[4]} from test PID loop {parameter[0]} on PT1000 {PREFIXES[parameter[1]]}{parameter[2]}")
            pid.set_temperature(parameter[0], 0)
            pid.enable(False)
            
    for idx, item in enumerate(correct):
        print(f"PID channel {idx} is: {'Correct' if item else 'Incorrect'}")