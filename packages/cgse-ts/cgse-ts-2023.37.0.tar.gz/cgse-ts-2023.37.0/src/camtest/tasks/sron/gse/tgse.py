
from camtest import end_observation
from camtest import start_observation
from camtest import execute
from camtest import building_block

from camtest.commanding import tgse, tcs
from camtest.commanding.tcs import OperatingMode
from gui_executor.exec import exec_ui
from gui_executor.utypes import ListList, List
from pathlib import Path

from gui_executor.exec import exec_ui, Directory

UI_MODULE_DISPLAY_NAME = "TGSE Test phases"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"


@exec_ui(display_name="Go to T. Max Non-OP",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_max_non_op():
    execute(sron_go_to_max_non_op,
            description="TP#1 To Max T NON-OP 40°C")

@exec_ui(display_name="Go to Min T. Non-OP",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_min_non_op():
    # CAM ON @ -35°C
    # CAM-TVPT-001
    # CAM OFF @ -95°C
    # Reach termal stabilization
    
    # Go to the minimum non-operational tempeature of the CAM (-110°C)
    execute(sron_go_to_min_non_op, 
            description="TP#2 To Min T. NON-OP -110°C")

@exec_ui(display_name="Go to T. Max OP",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_max_op():
    # CAM ON @ -95°C
    # CAM-TVPT-001
    # Reach termal stabilization
    
    
    # Go to the maximum operational tempeature of the CAM (-65°C)
    execute(sron_go_to_max_op,
            description="TP#3 To T OP -65°C")

@exec_ui(display_name="Go to -70°C",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_op_70():
    # CAM-TVPT-010
    # Reach termal stabilization
    
    # Go to the operational tempeature of the CAM (70°C)
    execute(sron_go_to_op_70,
            description="TP#4 To T OP -70°C")

@exec_ui(display_name="Go to -75°C",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_op_75():
    # Reach termal stabilization
    # CAM-TVPT-010
    
    # Go to the operational tempeature of the CAM (-75°C)
    execute(sron_go_to_op_75,
            description="TP#6 To T OP -75°C")

@exec_ui(display_name="Go to -80°C",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_op_80():
    # Reach termal stabilization
    # CAM-TVPT-010
    # Go to the operational tempeature of the CAM (-80°C)
    execute(sron_go_to_op_80,
            description="TP#8 To T OP -80°C")

@exec_ui(display_name="Go to -85°C",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_op_85():
    # Reach termal stabilization
    # CAM-TVPT-010
    
    # Go to the operational tempeature of the CAM (-85°C)
    execute(sron_go_to_op_85,
            description="TP#10 To T OP -85°C")

@exec_ui(display_name="Go to -90°C",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_op_90():
    # Reach termal stabilization
    # CAM-TVPT-010

    # Go to the operational tempeature of the CAM (-90°C)
    execute(sron_to_op_90,
            description="TP#12 To T. OP -90°C")

@exec_ui(display_name="Go to T. Min OP",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_min_op():
    # Reach termal stabilization
    # CAM-TVPT-031 Internal sync
    # CAM-TVPT-110 
    # CAM-TVPT-031 External Sync
    # CAM-TVPT-110
    # CAM-TVPT-100
    
    # Go to the maximum operational tempeature of the CAM (-95°C)
    execute(sron_go_min_op,
            description="TP#14 To Min T. OP -95°C")


@exec_ui(display_name="Go to decontamination",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_decontamination():
    # CAM ON
    
    # Go to the maximum operational tempeature of the CAM (-95°C)
    execute(sron_go_to_decontamination,
            description="TP#17a Decontamination")


@exec_ui(display_name="Go to warmup",
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def go_to_warmup():
    # CAM OFF @ -65°C
    
    # Go to the maximum operational tempeature of the CAM (-95°C)
    execute(sron_go_to_warmup, 
            description="TP#17b Warmup")



@building_block
def sron_go_to_max_non_op():
    
    # Reach termal stabilization
    # Go to the maximum operational tempeature of the CAM (65°C)
    print("Going to TP#1: Max T NON-OP 40°C")
    print("Setting TRP1 to: 40, TRP2 t0: 40")
    # Set Cam TGSE
    _sron_set_tgse_setpoint(trp1 = 40., 
                            trp22 = 40.)

@building_block
def sron_go_to_min_non_op():
    # CAM ON @ -35°C
    # CAM-TVPT-001
    # CAM OFF @ -95°C
    # Reach termal stabilization
    
    # Go to the minimum non-operational tempeature of the CAM (-110°C)
    print("Going to TP#2: Min T. NON-OP -110°C")
    print("Setting TRP1 to: -110, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -105")
    
    _sron_set_tgse_setpoint(trp1 = -110.,
                            trp22 = -35.,
                            teb_sky = -180., 
                            teb_tou = -180.,
                            teb_fee = -45., 
                            mari = -105.)
@building_block
def sron_go_to_max_op():
    # CAM ON @ -95°C
    # CAM-TVPT-001
    # Reach termal stabilization
    
    
    # Go to the maximum operational tempeature of the CAM (-65°C)
    print("Going to TP#3: T. OP -65°C")
    print("Setting TRP1 to: -65, TRP2 to: -40")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    _sron_set_tgse_setpoint(trp1=-65., 
                            trp22=-40., 
                            teb_sky=-180., 
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)
@building_block
def sron_go_to_op_70():
    # Reach termal stabilization
    # CAM-TVPT-010

    print("Going to TP#4: T. OP -70°C")
    print("Setting TRP1 to: -70, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-70.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)

@building_block
def sron_go_to_op_75():
    # Reach termal stabilization
    # CAM-TVPT-010

    print("Going to TP#6: T. OP -75°C")
    print("Setting TRP1 to: -75, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-75.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)
  
@building_block
def sron_go_to_op_80():
    # Reach termal stabilization
    # CAM-TVPT-010
    # Go to the operational tempeature of the CAM (-80°C)

    print("Going to TP#8: T. OP -80°C")
    print("Setting TRP1 to: -80, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-80.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)

@building_block
def sron_go_to_op_85():
    # Reach termal stabilization
    # CAM-TVPT-010

    # Go to the operational tempeature of the CAM (-85°C)
    print("Going to TP#10: T OP -85°C")
    print("Setting TRP1 to: -85, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-85.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)
 
@building_block
def sron_to_op_90():
    # Reach termal stabilization
    # CAM-TVPT-010

    print("Going to TP#12: T. OP -90°C")
    print("Setting TRP1 to: -90, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-90.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)
    

@building_block
def sron_go_min_op():
    # Reach termal stabilization
    # CAM-TVPT-031 Internal sync
    # CAM-TVPT-110 
    # CAM-TVPT-031 External Sync
    # CAM-TVPT-110
    # CAM-TVPT-100
    
    # Go to the maximum operational tempeature of the CAM (-95°C)
    print("Going to TP#14: Min T. OP -95°C")
    print("Setting TRP1 to: -95, TRP2 to: -35")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: -77")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-95.,
                            trp22=-35.,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=-77.)


@building_block
def sron_go_to_decontamination():
    print("Going to TP#17a: Decontamination")
    print("Setting TRP1 to: -10, TRP2 off")
    print("Setting TEB_SKY to: -180")
    print("Setting TEB_TOU to: -180")
    print("Setting TEB_FEE to: -45")
    print("Setting MaRi to: 20")
    
    # Set facility TGSE
    _sron_set_tgse_setpoint(trp1=-10.,
                            trp22=None,
                            teb_sky=-180.,
                            teb_tou=-180.,
                            teb_fee=-45.,
                            mari=20.)

@building_block
def sron_go_to_warmup():
    # CAM OFF @ -65°C
    
    # Go to the maximum operational tempeature of the CAM (-95°C)
    print("Going to TP#17b: Warmup")
    print("Setting TRP1 to: 25, TRP2 to: 25")
    print("Setting TEB_SKY to: 20")
    print("Setting TEB_TOU to: 20")
    print("Setting TEB_FEE to: 20")
    print("Setting MaRi to: 25")
    
    _sron_set_tgse_setpoint(trp1=25., 
                            trp22=25.,
                            teb_sky=20.,
                            teb_tou=20.,
                            teb_fee=20.,
                            mari=25.)

def _sron_set_tgse_setpoint(trp1, trp22, teb_sky=None, teb_tou=None, teb_fee=None, mari=None):
    # Set facility TGSE
    
    if teb_sky != None:
        tgse.set_temp_setpoint(trp=tgse.TRP.TEB_SKY, temperature= teb_sky)
        tgse.start_control(trp=tgse.TRP.TEB_SKY)
    
    if teb_tou != None:
        tgse.set_temp_setpoint(trp=tgse.TRP.TEB_TOU, temperature= teb_tou)
        tgse.start_control(trp=tgse.TRP.TEB_TOU)
        
    if teb_fee != None:
        tgse.set_temp_setpoint(trp=tgse.TRP.TEB_FEE, temperature= teb_fee)
        tgse.start_control(trp=tgse.TRP.TEB_FEE)
    
    if mari != None:
        tgse.set_temp_setpoint(trp=tgse.TRP.TRP2, temperature= mari)
        tgse.set_temp_setpoint(trp=tgse.TRP.TRP3, temperature= mari)
        tgse.set_temp_setpoint(trp=tgse.TRP.TRP4, temperature= mari)
        tgse.start_control(trp=tgse.TRP.TRP2)
        tgse.start_control(trp=tgse.TRP.TRP3)
        tgse.start_control(trp=tgse.TRP.TRP4)
    
    # Set Cam TGSE
    tcs.stop_task()
    tcs.set_operating_mode(mode=OperatingMode.EXTENDED)
    tcs.set_trp1(temperature=trp1)
    tcs.set_trp22(temperature=trp22)
    tcs.start_task()
    
