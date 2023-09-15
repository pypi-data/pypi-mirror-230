from time       import sleep
from datetime   import datetime
from typing     import List

from egse.state import GlobalState

from camtest import end_observation
from camtest import start_observation
from camtest import execute
from camtest import building_block

from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "Facility GSE"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

def confirmation_option() -> List:
    return [True, False]

def default_choice() -> bool:
    return False


@exec_ui(display_name="Start facility pumpdown",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def start_pumpdown():
    try:
        turbopump   = GlobalState.setup.gse.tc400.device
        scrollpump   = GlobalState.setup.gse.acp40.device
        valves      = GlobalState.setup.gse.beaglebone_vacuum.device
        firstgauge  = GlobalState.setup.gse.igm402.device
        secondgauge = GlobalState.setup.gse.tpg261.device
    except Exception as ex:
        print(f"Could not connect to proxies: {ex}")
        return
    
    
    execute(sron_facility_pump_down,
            scrollpump=scrollpump,
            turbopump=turbopump,
            valves=valves,
            firstgauge=firstgauge,
            secondgauge=secondgauge,
            description="Starting facility pumpdown")


@exec_ui(display_name="Stop facility pumps",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def stop_pumpdown():
    try:
        turbopump   = GlobalState.setup.gse.tc400.device
        scrollpump   = GlobalState.setup.gse.acp40.device
        valves      = GlobalState.setup.gse.beaglebone_vacuum.device
        gauge       = GlobalState.setup.gse.igm402.device
    except Exception as ex:
        print(f"Could not connect to proxies: {ex}")
        return
    
    
    execute(sron_facility_pump_shutdown,
            gauge=gauge,
            scrollpump=scrollpump,
            turbopump=turbopump,
            valves=valves,
            description="Stopping facility pumpdown")


@exec_ui(display_name="Start RGA scan",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def start_rga_scan(startMass: int=range(200),
                   endMass: int=range(200),
                   numScans: int=range(999)):
    
    try:
        rga = GlobalState.setup.gse.evison.device
    except Exception as ex:
        print('[red]Could not connect to proxies')
    
    execute(sron_rga_start_scan,
            rga=rga,
            startMass=startMass,
            endMass=endMass,
            numScans=numScans,
            description=f"Start RGA scan, Start: {startMass}, End:{endMass}, Number of scans: {numScans}")
    

    
@exec_ui(display_name="Stop RGA scan",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def stop_rga_scan():
    
    try:
        rga = GlobalState.setup.gse.evison.device
    except Exception as ex:
        print('[red]Could not connect to proxies')
    
    execute(sron_rga_stop_scan,
            rga=rga,
            description="Stopping RGA scan")
    


@exec_ui(display_name="Replace LN2 - Close",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def close_ln2_valves(confirm: Callback(confirmation_option, name=List, default=default_choice)):
    if confirm:
        try:
            valves = GlobalState.setup.gse.beaglebone_vacuum.device
        except Exception as ex:
            print("[red]Could not connect to proxies")
        
        execute(sron_close_ln2_valves, 
                valves=valves, 
                description="Closing LN2 valves")
    else:
        print("[red]Method needs confirmation")
    
@exec_ui(display_name="Replace LN2 - Open",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def open_ln2_valves(confirm: Callback(confirmation_option, name=List, default=default_choice)):
    if confirm:
        try:
            valves = GlobalState.setup.gse.beaglebone_vacuum.device
        except Exception as ex:
            print("[red]Could not connect to proxies")
        
        execute(sron_open_ln2_valves, 
                valves=valves, 
                description="Opening LN2 valves")
    else:
        print('[red]Method needs confirmation')

@exec_ui(display_name="Start Scrollpump",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def start_scrollpump():
    try:
        scrollpump = GlobalState.setup.gse.acp40.device
    except Exception as ex:
        print("[red]Could not connect to proxies")
    
    execute(sron_start_scrollpump, 
            scrollpump=scrollpump, 
            description="Starting scrollpump")
    
@exec_ui(display_name="Stop Scrollpump",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def stop_scrollpump(confirm: Callback(confirmation_option, name=List, default=default_choice)):
    if confirm:
        try:
            scrollpump = GlobalState.setup.gse.acp40.device
        except Exception as ex:
            print("[red]Could not connect to proxies")
        
        execute(sron_stop_scrollpump, 
                scrollpump=scrollpump, 
                description="Stopping scrollpump")
    else:
        print("[red]Method needs confirmation")

@exec_ui(display_name="Start turbopump",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def start_turbopump():
    try:
        turbopump = GlobalState.setup.gse.tc400.device
    except Exception as ex:
        print("[red]Could not connect to proxies")
    
    execute(sron_start_turbopump, 
            turbopump=turbopump, 
            description="Starting turbopump")

@exec_ui(display_name="Stop Turbopump",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def stop_turbopump(confirm: Callback(confirmation_option, name=List, default=default_choice)): 
    if confirm:
        try:
            turbopump = GlobalState.setup.gse.tc400.device
        except Exception as ex:
            print("[red]Could not connect to proxies")
        
        execute(sron_stop_turbopomp, 
                turbopump=turbopump, 
                description="Stopping turbopump")
    
    else:
        print("[red]Method needs to be confirmed")

@exec_ui(display_name="Turn on Ion Gauge",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def turn_on_iongauge(confirm: Callback(confirmation_option, name=List, default=default_choice)):
    if confirm:
        try:
            gauge = GlobalState.setup.gse.igm402.device
        except Exception as ex:
            print("[red]Could not connect to proxies")
        
        execute(sron_turn_on_ion_gauge, 
                gauge=gauge, 
                description="Turning on ion gauge")
    else:
        print("[red]Method needs to be confirmed")

@exec_ui(display_name="Turn off Ion Gauge",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def turn_off_iongauge():
    try:
        gauge = GlobalState.setup.gse.igm402.device
    except Exception as ex:
        print("[red]Could not connect to proxies")
    
    execute(sron_turn_off_ion_gauge, 
            gauge=gauge, 
            description="Turning off ion gauge")

@exec_ui(display_name="Open gate valve",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def open_gate_valve():
    try:
        valves = GlobalState.setup.gse.beaglebone_vacuum.device
    except Exception as ex:
        print("[red]Could not connect to proxies")
    
    execute(sron_open_gate_valve, 
            valves=valves, 
            description="Opening gate valve")
    
@exec_ui(display_name="Close gate valve",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def close_gate_valve():
    try:
        valves = GlobalState.setup.gse.beaglebone_vacuum.device
    except Exception as ex:
        print("[red]Could not connect to proxies")
    
    execute(sron_open_gate_valve, 
            valves=valves, 
            description="Closing gate valve")

@building_block
def sron_rga_start_scan(rga, startMass=1, endMass=200, numScans=10):
    rga.filament_control(True)
    
    print("Turning on filament")
    while 'ON' not in rga.get_filament_status():
        print(f"Current filament status: {rga.get_filament_status()}", end='\r')
        sleep(1)
    
    name = datetime.now().strftime("%d%m%Y%H%M%S")
    
    rga.add_bar_chart(name=f"Bar_{name}",
                      startMass=startMass,
                      endMass=endMass,
                      filterMode='PeakCenter',
                      accuracy=5,
                      eGainIndex=0,
                      sourceIndex=0,
                      detectorIndex=0)
    
    rga.start_scan(numScans)


@building_block
def sron_rga_stop_scan(rga):
    rga.stop_scan()
    rga.measurement_remove_all()
    
    rga.filament_control(False)
   
@building_block
def sron_open_ln2_valves(valves):
    ln_valves = ['MV011', 'MV012', 'MV013', 'MV014']
    
    for valve in ln_valves:
        valves.set_valve(valve, True)
        sleep(120)

@building_block
def sron_close_ln2_valves(valves):
    ln_valves = ['MV011', 'MV012', 'MV013', 'MV014']
    
    for valve in ln_valves:
        valves.set_valve(valve, False)
        sleep(0.5)

@building_block
def sron_open_gate_valve(valves):
    print("[green]Opening gate valve...")
    
    try:
        valves.set_valve('MV001', True)
    except Exception as ex:
        print(f"[red]Could not open Gate valve")
        raise Exception(f"Could not open Gate valve: {ex}")
    else:
        # Wait until valve is opened
        sleep(7) 

@building_block
def sron_close_gate_valve(valves):
    print("[green]Closing gate valve...")
    
    try:
        valves.set_valve('MV001', True)
    except Exception as ex:
        print(f"[red]Could not close Gate valve")
        raise Exception(f"Could not close Gate valve: {ex}")
    else:
        # Wait until valve is opened
        sleep(7) 

@building_block
def sron_start_turbopump(turbopump):
    print('[green]Starting turbopump...')
    try:
        turbopump.set_pumpingstation(enable=True)
        turbopump.set_motorpump(enable=True)
    except Exception as ex:
        print(f"[red]Could not start turbo pump")
        raise Exception(f"Could not start turbo pump: {ex}")

@building_block
def sron_stop_turbopomp(turbopump):
    print('[green]Shuting down turbopump...')
    turbopump.set_pumpingstation(enable=False)

    print('Waiting for tc400 to reach 50 Hz...')
    speed = turbopump.get_active_speed()
    while (speed > 50):
        speed = turbopump.get_active_speed()
        print(f'Current turbopump speed: {speed:.2f} Hz', end='\r')
        sleep(2)

@building_block
def sron_start_scrollpump(scrollpump):
    print('[green]Starting scrollpump...')
    for i in range(2):
        try:
            scrollpump.set_enable(enable=True)
        except Exception as ex:
            print(f"[red]Could not start scroll pump")
            if i == 2:
                raise Exception(f"Could not start scrollpump: {ex}")
            print("[red]Retrying....")
        else:
            break
        
@building_block
def sron_stop_scrollpump(scrollpump):
    print('[green]Stopping scrollpump...')
    for i in range(2):
        try:
            scrollpump.set_enable(enable=False)
        except Exception as ex:
            print(f"[red]Could not stop scroll pump")
            if i == 2:
                raise Exception(f"Could not stop scrollpump: {ex}")
            print("[red]Retrying....")
        else:
            break

@building_block
def sron_turn_on_ion_gauge(gauge):
    print('[green]Turning on ionization gauge...')
    try:
        gauge.set_filament_enable(enable=True)
    except Exception as ex:
        print(f"[red]Could not turn on ion gauge")
        raise Exception(f"Could not turn on ion gauge: {ex}")
    
@building_block
def sron_turn_off_ion_gauge(gauge):
    print('[green]Turning off ionization gauge...')
    try:
        gauge.set_filament_enable(enable=False)
    except Exception as ex:
        print(f"[red]Could not turn off ion gauge")
        raise Exception(f"Could not turn off ion gauge: {ex}")

@building_block
def sron_wait_for_pressure(firstgauge, secondgauge, pressure, redundant=False, ion=False):
    while True:
        try:
            if not ion:
                firstgauge_p = firstgauge.get_cgn_pressure(1)
            else:
                firstgauge_p = firstgauge.get_ion_gauge_pressure()
                
            if redundant:
                sencondgauge_p = secondgauge.get_gauge_pressure()
            else:
                secondgauge_p = firstgauge_p
            if not isinstance(firstgauge_p, float) and not isinstance(sencondgauge_p, float):
                print(f"[red]Invalid datatype from gauges - igm402: {firstgauge_p:.3e}"\
                    f"[red]{' tpg261: ' if redundant else ''} {sencondgauge_p if redundant else '':.3e}")
                sleep(10)
                continue
            else:
                if (firstgauge_p < pressure) and (sencondgauge_p < pressure):
                    break
                
        except Exception as ex:
            print(f"[red]Could not retrieve valid HK: {ex}")
        else:
            print(f"Current pressures: {firstgauge_p:.3e} {sencondgauge_p:.3e}", end='\r')
        finally:
            sleep(5)
    print(f"[green]Target pressure reached: ({firstgauge.get_cgn_pressure(1) if not ion else firstgauge.get_ion_gauge_pressure():.3e}):")

@building_block
def sron_facility_pump_down(scrollpump, turbopump, valves, firstgauge, secondgauge):

    try:
        sron_open_gate_valve(valves)
    except Exception as ex:
        print("[red]Stopping pumpdown")
        raise ex

    # Start scrollpump
    try:
        sron_start_scrollpump(scrollpump)
    except Exception as ex:
        print("[red]Stopping pumpdown")
        raise ex

    print('Waiting for pressure to reach 6E-0 mbar...')

    sron_wait_for_pressure(firstgauge, secondgauge, 6E-0)

    # Start turbopump
    try:
        sron_start_turbopump(turbopump)
    except Exception as ex:
        print("[red]Stopping pumpdown")
        raise ex    

    print('Waiting for pressure to reach 1.1E-3 mbar...')
    
    sron_wait_for_pressure(firstgauge, secondgauge, 1.1E-3, redundant=True)
    
    # Turn on ion gauge
    try:
        sron_turn_on_ion_gauge(firstgauge)
    except Exception as ex:
        print("[red] Could not turn on ion gauge, please turn on manually")
        print("[red] Exiting pumpdown, not ready for cooling. please restart pumpdown script")
        raise ex

    print('Waiting for pressure to reach 1E-5 mbar...')
    
    sron_wait_for_pressure(firstgauge, secondgauge, 1E-5, redundant=True, ion=True)

    print('Ready for cooling')


@building_block
def sron_facility_pump_shutdown(gauge, turbopump, scrollpump, valves):
    # Closing gate valve
    try:
        sron_close_gate_valve(valves)
    except Exception as ex:
        print("[red]Stopping pump shutdown")
        raise ex

    # Turning off ion gauge
    try:
        sron_turn_off_ion_gauge(gauge)
    except Exception as ex:
        print("[red] Could not turn off ion gauge, please turn off manually")
        print("[red] Exiting pump shutdown. please restart pump shutdown script")
        raise ex

    # Shutting down turbopump and waiting for rampdown
    try:
        sron_stop_turbopomp(turbopump)
    except Exception as ex:
        print("[red]Stopping pump shutdown")
        raise ex

    try:
        sron_stop_scrollpump(scrollpump)
    except Exception as ex:
        print("[red]Stopping pump shutdown")

    print('Shutdown complete')