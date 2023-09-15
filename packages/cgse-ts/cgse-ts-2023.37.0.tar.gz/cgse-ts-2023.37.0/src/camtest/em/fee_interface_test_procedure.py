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
from egse.exceptions import Abort

"""
########################################
### SWON
########################################

From procedure PLATO-KUL-PL-TP-0004, SWON:
0010 egse server : ON
0020 egse desktop : ON
0030 AEU : ON
0050 DAQ : ON
0070 mechanism controllers : ON
0080 OGSE : ON
0090 SpW I/F : ON
0120 Launch pm_ui on the client (desktop icon)
         the leds for the core services should be green
0130 terminal open on the server
0140 start the daq control server on the server
        needs to be done on the command line, instead of via the PM UI
        (for some reason the button in the PM doesn't do the trick)
0150 start the cm_ui on the client (click on the GUI button for the CM in the PM UI)
0160 setup_ui (click on the button in the toolbar of the CM UI)
0170 Load the setup in the setup UI (don't you love the little truck?)
        the setup will be shown in the CM UI and the devices listed in the setup will show up in the PM UI
        the led for the DAQ should be green (as you already started it in step 0140)
0190 launch the data acquisition system for the DAQ on the server
0200 start all control servers from the pm_ui, except the DPU
        there's a button in the toolbar to start all AEU CS in one go
        I would insert here:
            - start the DPU CS (can only be done from the command line):
                    dpu_cs start --zeromq
            - before or right after the DPU CS has been started, you need to start the DPU UI (otherwise it hangs)
                    dpu_ui (remind me to make sure there's a button in the PM UI to do this)
            - start the FITS generator by pressing the button in the toolbar of the PM UI (alternative: fitgen start)
        all leds in the PM UI should be green now
        HK should be coming in for all devices (and core services)
0210 pycharm
"""

### 0220 [procedure PLATO-KUL-PL-TP-0004, SWON]
### IMPORTS
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle, system_to_initialized, system_test_if_initialized

from camtest import load_setup, execute
from rich import print
from camtest import start_observation, end_observation


### 0230 [procedure PLATO-KUL-PL-TP-0004, SWON]
### LOAD THE SETUP
setup = load_setup()
print(setup)

### 0260 [procedure PLATO-KUL-PL-TP-0004, SWON]
### Visual checks you can perform after these two commands:
###     - Front panel of the AEU
###     - AEU UI (press the GUI button in the PM UI next to one of the cRIO devices)
###     - N-AEU dashboard (Grafana)

### AEU SWON
execute(aeu.n_cam_swon)

### AEU ENABLE SYNC SIGNAL
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=1)

# Further down the script, we check whether the system is initialised/idle, which will check whether the six power
# lines are on for the N-CAM and the sync signal is being sent for the N-CAM.  This can only be the case when no
# errors (e.g. voltage/current out of range, sync generator error) have occurred, so we do not need to check this
# explicitly at this point.

# finetime, hk  = get_housekeeping(hk_name="",time_window=600)

"""
Sara: 20211308: AEU checklist: system_test_if_initialized  and system_test_if_idle check whether the six power lines 
are on and sync pulses are being sent. I actually don’t think you need additional checks in your script 
(at least not for the AEU).  It’s impossible to switch on the power lines / sync signals when one of the errors occur 
(and idle/initialised would fail anyway).
"""

### 0270 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE DPU CONTROL SERVER (see remark in step 0200 at the top of this file)
"""
$ dpu_cs start --zeromq
"""
### 0280 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE DPU_UI on the client (must happen right after dpu_cs; see remark in step 0200 at the top of this file)
"""
$dpu_ui
"""

### 0290 [procedure PLATO-KUL-PL-TP-0004, SWON]
### START THE FITS GENERATOR (see remark in step 0200 at the top of this file)
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

# The CM should tell you which obsid is running (+ red border)

### N-FEE to ON MODE
### N-FEE ON, CCDs NOT POWERED

# 0510 : AEU SWON puts the FEEs in on mode --> is_on_mode should return True already
if not dpu.n_cam_is_on_mode():

    raise Abort("N-FEE should go to on mode when the AEU is switched on")

# 0520 : go to on mode
dpu.n_cam_to_on_mode()

# 0530 : is_on_mode should return True
if not dpu.n_cam_is_on_mode():

    raise Abort("Putting the N-FEE in on mode did not succeed")

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

# The border of the CM UI will become green again


###
### STANDBY MODE
###


# 0600 START OBSERVATION
start_observation("FEE Checkout : STANDBY MODE")

# The CM should tell you which obsid is running (+ red border)

### N-FEE to STANDBY MODE
### N-FEE ON, CCDs POWERED

# 0610 : is_standby_mode should return False
if dpu.n_cam_is_standby_mode():

    raise Abort("N-FEE should not be in stand-by mode")

# 0620 : go to standby mode
dpu.n_cam_to_standby_mode()

# 0630 : is_standby_mode should return True
if not dpu.n_cam_is_standby_mode():

    raise Abort("Putting the N-FEE in stand-by mode did not succeed")

# Success criteria : TBD

# 0640 : END OBSERVATION, close the obsid
end_observation()

# The border of the CM UI will become green again

###
### DUMP MODE AND IDLE STATE
###


# 0650 START OBSERVATION
start_observation("FEE Checkout : DUMP MODE and system IDLE state")

# The CM should tell you which obsid is running (+ red border)

### N-FEE to DUMP MODE
### N-FEE full-image mode + dumping the data

# 0700 : is_dump_mode should return False
if dpu.n_cam_is_dump_mode():

    raise Abort("N-FEE should not be in dump mode")

# 0710 : go to dump mode
dpu.n_cam_to_dump_mode()

# 0720 : is_dump_mode should return True
if not dpu.n_cam_is_dump_mode():

    raise Abort("Putting the N-FEE in dump mode did not succeed")

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

# The border of the CM UI will become green again




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

# In the /obs directory you should find two FITS files:
#   <setup ID>_CSL_<obsid>_CCD_<date>_<time>_00001.fits -> Flat structure
#   <setup ID>_CSL_<obsid>_CCD_<date>_<time>_cube_00001.fits -> Cube structure
# You can use the convenience functions from camtest.analysis.functions.fitsfiles to inspect these

# primary_header = get_primary_header(filename)
# primary_header["V_START"] should equal row_start
# primary_header["V_END"] should equal row_end
# primary_header["H_END"] should equal the number of columns (2295?)
# primary_header["OBSID"] should equal the obsid that was shown in the CM UI while the observation was running

# E.g. to check whether you have the expected number of exposures:
# image_header = get_image_cube_header(filename for the cubes, ccd_number, ccd_side)
# image_header["NAXIS3"] should equal the expected number of exposures
#    This is the way you can access the values of the keys in the headers (see also the commanding manual)

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
# Expected number of exposures for (1, E): 3 (num_cycles) * 4 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (2, E): 5 (num_cycles) * 4 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (1/2/3/4, E): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)

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
# Expected number of exposures for (1/2/3/4, F): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)

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
# Expected number of exposures for (4, E/F): 3 (num_cycles) * 4 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (4, E/F): 3 (num_cycles) * 4 (as often as you read out this CCD per cycle)

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
# Expected number of exposures for (4, E): 3 (num_cycles) * 4 (as often as you read out this CCD per cycle)

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
# Expected number of exposures for (1/2/3/4, E/F): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (1/2/3/4, E/F): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (1/2/3/4, F): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)


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
# Expected number of exposures for (1/2/3/4, E): 3 (num_cycles) * 1 (as often as you read out this CCD per cycle)


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
if not dpu.n_cam_is_dump_mode():

    raise Abort("N-FEE should be in dump mode")

# 1110 Activate internal sync --> specific dump_mode_int_sync
dpu.n_cam_to_dump_mode_int_sync()

# 1120 Check this mode is recognized as dump mode
dpu.n_cam_is_dump_mode()

# 1130 Go back to FEE STANDBY MODE
dpu.n_cam_to_standby_mode()

# 1140 Check starting conditions : standard dump mode -- should return False
if dpu.n_cam_is_dump_mode():

    raise Abort("Putting the N-FEE in dump mode did not succeed")

# 1150 Activate internal sync --> specific dump_mode_int_sync
execute(dpu.n_cam_to_dump_mode_int_sync)

# 1160 Check this mode is recognized as dump mode
if not dpu.n_cam_is_dump_mode():

    raise Abort("Putting the N-FEE in dump mode did not succeed")

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

# The CM should tell you which obsid is running (+ red border)

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

if dpu.n_cam_is_dump_mode():

    raise Abort("N-FEE should not be in stand-by mode")


# 1520 Break the loop
dpu.n_cam_to_dump_mode_int_sync()

# 1530 Check FEE status : is_dump_mode should return True
#      Check for dump_mode_int_sync parameters (cycle_time, rows_final_dump, dump_gate)
if not dpu.n_cam_is_dump_mode():

    raise Abort("Putting the N-FEE in dump mode did not succeed")

# 1540 end_observation
end_observation()

# The border of the CM UI will become green again
