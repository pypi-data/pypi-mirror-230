"""
EM ANALOG CHAIN CHECKOUT and NFEE INTERFACE VALIDATION TEST
AMBIENT
CSL

Reference documents:
RD01 PLATO-KUL-PL-TP-0004 - CSL GSE SWON procedure
RD02 PLATO-KUL-PL-TP-0010_CAM-AFT-010_AnalogChainFunctionalAmbient
RD03 PLATO-KUL-PL-MAN-0004_v0.5_CameraGroundTestCommandingManual

Authors : Plato team @ KUL

History : 2021 08 13 v1.

"""

### STARTING CONDITIONS : SWON PROCEDURE EXECUTED UNTIL THE FIRST PYTHON COMMANDS:

"""
########################################
### SWON
########################################

From procedure PLATO-KUL-PL-TP-0004, SWON:
0010 egse server : ON
0020 egse desktop : ON
0030 AEU : ON
0050 DA : ON
0070 mechanism controllers : ON
0080 OGSE : ON
0090 SpW I/F : ON
0120 Launch pm_ui on the client
0130 terminal open on the server
0140 start the daq control server
0150 start the cm_ui on teh client
0160 setup_ui
0170 Load the setup
0190 launch the data acquisition system for the DAQ on the server
0200 start all control servers from the pm_ui, except the DPU
0210 pycharm
"""

from rich import print

from camtest import load_setup, execute
from camtest import start_observation, end_observation
### 0220 [procedure PLATO-KUL-PL-TP-0004, SWON]
### IMPORTS
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle, system_to_initialized, system_test_if_initialized

### 0230 [procedure PLATO-KUL-PL-TP-0004, SWON]
### LOAD THE SETUP
setup = load_setup()
print(setup)


### 0260 [procedure PLATO-KUL-PL-TP-0004, SWON]
### AEU SWON
execute(aeu.n_cam_swon)

from egse.aeu.aeu import CRIOProxy, OperatingMode

crio = CRIOProxy()
crio.set_operating_mode(0)

execute(aeu.n_cam_swoff)

crio.set_operating_mode(OperatingMode.FC_TVAC)

execute(aeu.n_cam_swoff)

execute(aeu.n_cam_swon)

from egse.aeu.aeu import PSUProxy

psu1 = PSUProxy(1)
psu2 = PSUProxy(2)
psu3 = PSUProxy(3)
psu4 = PSUProxy(4)
psu5 = PSUProxy(5)
psu6 = PSUProxy(6)

psu = [None, psu1, psu2, psu3, psu4, psu5, psu6]

psu6.set_ocp(1.59)

execute(aeu.n_cam_swoff)

execute(aeu.n_cam_swon)

crio.get_error_info()
crio.get_num_errors()

execute(aeu.n_cam_swon)

crio.get_num_errors()
crio.get_protection_status()

for idx in range(1, 7):
    print(f"PSU{idx}: {psu[idx].get_error_info()}, {psu[idx].questionable_status_register()}")

### AEU ENABLE SYNC SIGNAL
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=1)

# Success Criteria: @Sara
# finetime, hk  = get_housekeepeing(hk_name="",time_window=600)

"""
Sara: 20211308: AEU checklist: system_test_if_initialized  and system_test_if_idle check whether the six power lines 
are on and sync pulses are being sent. I actually don’t think you need additional checks in your script 
(at least not for the AEU).  It’s impossible to switch on the power lines / sync signals when one of the errors occur 
(and idle/initialised would fail anyway).
"""

### 0270 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE DPU CONTROL SERVER
"""
$ dpu_cs start --zeromq
"""
### 0280 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE DPU_UI on the client (must happen right after dpu_cs)
"""
$dpu_ui
"""

### 0290 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE FITS GENERATOR (Button in the pm_ui)
"""
# Alternative:
$fitsgen start
"""

########################################
### FEE Functional Check
########################################

# START procedure PLATO-KUL-PL-TP-0010



###
### ON MODE AND INITIALIZED STATE
###



# 0500 START OBSERVATION : launch an OBSID to cover the basic manual commanding at the start
start_observation("FEE Checkout : FEE ON mode & system INITIALIZED state")


### N-FEE to ON MODE
### N-FEE ON, CCDs NOT POWERED

# 0510 : AEU SWON puts the FEEs in on mode --> is_on_mode should return True already
dpu.n_cam_is_on_mode()

# 0520 : go to on mode
dpu.n_cam_to_on_mode()

# 0530 : is_on_mode should return True
dpu.n_cam_is_on_mode()

# Success criteria : TBD


### SYSTEM TO INITIALIZED STATE
### Bring the overal system into a reference state
### FEEs in ON_MODE, OGSE lamp on, all devices up and ready

# 0550 system_to_initialized
system_to_initialized()

# Success criteria : TBW

# 0560 system_test_if_initialized
system_test_if_initialized()


# 0570 : END OBSERVATION, close the obsid
end_observation()


###
### STANDBY MODE
###


# 0600 START OBSERVATION
start_observation("FEE Checkout : STANDBY MODE")

### N-FEE to STANDBY MODE
### N-FEE ON, CCDs POWERED

# 0610 : is_standby_mode should return False
dpu.n_cam_is_standby_mode()

# 0620 : go to standby mode
dpu.n_cam_to_standby_mode()

# 0630 : is_standby_mode should return True
dpu.n_cam_is_standby_mode()

# Success criteria : TBD

# 0640 : END OBSERVATION, close the obsid
end_observation()



###
### DUMP MODE AND IDLE STATE
###


# 0650 START OBSERVATION
start_observation("FEE Checkout : DUMP MODE and system IDLE state")


### N-FEE to DUMP MODE
### N-FEE full-image mode + dumping the data

# 0700 : is_dump_mode should return False
dpu.n_cam_is_dump_mode()

# 0710 : go to dump mode
dpu.n_cam_to_dump_mode()

# 0720 : is_dump_mode should return True
dpu.n_cam_is_dump_mode()

# Success criteria : TBD


### 0660 SYSTEM TO IDLE
### initialized system + full image mode, dumping the data

# 0730 system_to_idle
system_to_idle()

# Success criteria : TBW

# 0740 system_test_if_idle
system_test_if_idle()


# 0750 : END OBSERVATION, close the obsid
end_observation()






########################################
### VALIDATION OF OBSERVING MODES
########################################


### EXT. SYNC. - FULL-IMAGE MODE
### CONFIGURABLE MODE : n_cam_partial_ccd

# 0810 one CCD, one side, partial readout
n_fee_parameters = dict(
    num_cycles=3,
    row_start=25,
    row_end=525,
    rows_final_dump=0,
    ccd_order=[4, 4, 4, 4],
    ccd_side='F',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0820 one CCD, one side, full image
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[1, 1, 1, 1],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0830 one CCD, one side, partial readout, including overscans
n_fee_parameters = dict(
    num_cycles=5,
    row_start=4000,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[2,2,2,2],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0840 all CCDs, E side, full image
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0850 all CCDs, F side, full image
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side='F',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)

###
### ccd_side = "BOTH"
###

# 0860 one CCD,BOTH sides, partial readout 1000 rows
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=999,
    rows_final_dump=0,
    ccd_order=[4, 4, 4, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0870 one CCD,BOTH sides, partial readout half CCDs
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=2254,
    rows_final_dump=0,
    ccd_order=[4, 4, 4, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)

# 0880 one CCD, BOTH sides, full CCDs
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[4, 4, 4, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0890 all CCDs, BOTH sides, half CCDs
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=2254,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0900 all CCDs, BOTH sides, half CCDs
n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


###
### CHANGE CCD ORDER
###

# 0910 all CCDs, F side, partial readout, CHANGE CCD ORDER

n_fee_parameters = dict(
    num_cycles=3,
    row_start=50,
    row_end=550,
    rows_final_dump=0,
    ccd_order=[3, 4, 1, 2],
    ccd_side='F',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


# 0920 all CCDs, E side, partial readout, CHANGE CCD ORDER
n_fee_parameters = dict(
    num_cycles=3,
    row_start=25,
    row_end=1025,
    rows_final_dump=0,
    ccd_order=[2, 3, 4, 1],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)


###
### CCD CLEAROUT
###

# 0930 one CCDs, BOTH sides, partial readout, FINAL CLEAROUT
n_fee_parameters = dict(
    num_cycles=5,
    row_start=25,
    row_end=1025,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)

# 0940 one CCDs, BOTH sides, full CCD, FINAL CLEAROUT
n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)

# 0950 all CCDs, E side, partial readout, FINAL CLEAROUT
n_fee_parameters = dict(
    num_cycles=5,
    row_start=25,
    row_end=1025,
    rows_final_dump=4510,
    ccd_order=[1, 2, 3, 4],
    ccd_side='E',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)

# 0960 all CCDs, BOTH side, full CCD, FINAL CLEAROUT
n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1, 2, 3, 4],
    ccd_side='BOTH',
)
execute(dpu.n_cam_partial_ccd, **n_fee_parameters)





### EXT. SYNC. - FULL-IMAGE MODE
### SIMPLIFIED MODE : n_cam_full_standard  &  n_cam_full_

# 1000 all CCDs, BOTH sides, full CCDs, standard order
n_fee_parameters = dict(
    num_cycles=5,
    ccd_side='BOTH',
)
execute(dpu.n_cam_full_standard, **n_fee_parameters)


# 1010 one CCD, BOTH sides, configuring the parallel overscan
n_fee_parameters = dict(
    num_cycles=5,
    ccd_order=[2, 2, 2, 2],
    ccd_side='BOTH',
    rows_overscan=20
)
execute(dpu.n_cam_full_ccd, **n_fee_parameters)


# 1020 all CCDs, BOTH sides, configuring the parallel overscan
n_fee_parameters = dict(
    num_cycles=5,
    ccd_order=[4, 3, 2, 1],
    ccd_side='BOTH',
    rows_overscan=30
)
execute(dpu.n_cam_full_ccd, **n_fee_parameters)





###
### FEE CHECKOUT - INTERNAL SYNC.
###

# 0990 START OBSERVATION
start_observation("FEE Checkout : FEE Internal Sync")

# 1100 Check starting conditions : standard dump mode
dpu.n_cam_is_dump_mode()

# 1110 Activate internal sync --> specific dump_mode_int_sync
dpu.n_cam_to_dump_mode_int_sync()

# 1120 Check this mode is recognized as dump mode
dpu.n_cam_is_dump_mode()

# 1130 Go back to FEE STANDBY MODE
dpu.n_cam_to_standby_mode()

# 1140 Check starting conditions : standard dump mode -- should return False
dpu.n_cam_is_dump_mode()

# 1150 Activate internal sync --> specific dump_mode_int_sync
execute(dpu.n_cam_to_dump_mode_int_sync)

# 1160 Check this mode is recognized as dump mode
dpu.n_cam_is_dump_mode()

# 1170 End observation
end_observation()


###
### Validation of internal sync observing modes
###

# 1200 Int. Sync, one CCD, E side, partial readout
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=500,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='E',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1210 Check end state of the system
# It should return to dump_mode_int_sync, i.e. cycle_time = 2.5 sec, dump gate high, rows_final_dump=4510 (TBC)
dpu.n_cam_is_dump_mode()


# 1220 Int. Sync, one CCD, F side, partial readout
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=500,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='F',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1230 Int. Sync, one CCD, BOTH sides, partial readout
# ADAPT EXPOSURE TIME FROM PREV. OBS. TO AVOID DARK SATURATION

nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=500,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1240 Int. Sync, one CCD, BOTH sides, partial readout higher --> impact on cycle_time
nfee_parameters = dict(
    num_cycles=10,
    row_start=3000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


# 1250 Int. Sync, one CCD, F side, partial readout incl. parallel overscan
nfee_parameters = dict(
    num_cycles=10,
    row_start=4240,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side='F',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


# 1260 Int. Sync, all CCDs, E side, partial readout
nfee_parameters = dict(
    num_cycles=10,
    row_start=1000,
    row_end=1500,
    rows_final_dump=4510,
    ccd_order=[2, 4, 3, 1],
    ccd_side='E',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


# 1270 Int. Sync, BOTH sides, partial readout, diff. exposure time / CCD
nfee_parameters = dict(
    num_cycles=10,
    row_start=2000,
    row_end=3000,
    rows_final_dump=4510,
    ccd_order=[1,1,1,3],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


# 1280 Int. Sync, all CCDs, E side, full CCD readout
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side='E',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


###
### DARK CURRENT @ AMBIENT
###

# 1310 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD1
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1,1,1,1],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1320 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD2
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1330 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD3
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1340 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD4
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='BOTH',
    exposure_time=4
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)


# Repeat with another exposure time
exposure_time = 8.

# 1410 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD1
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1,1,1,1],
    ccd_side='BOTH',
    exposure_time=exposure_time
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1420 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD2
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side='BOTH',
    exposure_time=exposure_time
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1430 Int. Sync, one CCDs, BOTH sides, full CCD readout  CCD3
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side='BOTH',
    exposure_time=exposure_time
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)

# 1440 Int. Sync, one CCD, BOTH sides, full CCD readout  CCD4
nfee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[4,4,4,4],
    ccd_side='BOTH',
    exposure_time=exposure_time
)
execute(dpu.n_cam_partial_int_sync, **nfee_parameters)





###
### Int sync infinite loop
###

# 1500 START OBSERVATION
start_observation("FEE Checkout : FEE Internal Sync Infinite Loop")

# 1510 Int. Sync, one CCD, BOTH sides, partial CCD readout, infinite loop
nfee_parameters = dict(
    num_cycles=0,
    row_start=1000,
    row_end=1500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side='BOTH',
    exposure_time=2
)

dpu.n_cam_partial_int_sync(**nfee_parameters)

# 1510 WAIT 2 minutes for the data acquisition, check for FEE status: is_dump_mode should return False
dpu.n_cam_is_dump_mode()


# 1520 Break the loop
dpu.n_cam_to_dump_mode_int_sync()

# 1530 Check FEE status : is_dump_mode should return True
#      Check for dump_mode_int_sync parameters (cycle_time, rows_final_dump, dump_gate)
dpu.n_cam_is_dump_mode()

# 1540 end_observation
end_observation()




