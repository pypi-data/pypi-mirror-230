"""
Purpose:

* Test OGSE and CAM commanding needed to be in the condition to start ambient recentering test script:
    * cam_aat_050_ambient_recentering.py
*

"""
import time

from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding import system_test_if_initialized
from egse.collimator.fcul.ogse import OGSEInterface

setup = load_setup()
print(setup)  # Setup 62

GlobalState.load_setup()
GlobalState.setup.get_id() # Setup 62


execute(aeu.n_cam_swon)  # 10:30

# Start the DPU_CS (server) and the DPU_UI (client)

execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)  # 10:37

# Start FITSGEN on the server




### N-FEE to ON MODE
### N-FEE ON, CCDs NOT POWERED

# 0510 : AEU SWON puts the FEEs in on mode --> is_on_mode should return True already
fee_mode = dpu.n_cam_is_on_mode()
print(f"{fee_mode=}")

# 0520 : go to on mode if needed
if not fee_mode:
    dpu.n_cam_to_on_mode()
    dpu.n_cam_is_on_mode()

# Success criteria : Voltage and Currents N-FEE are as expected



### SYSTEM TO INITIALIZED STATE
### Bring the overal system into a reference state
### FEEs in ON_MODE, OGSE lamp on, all devices up and ready

# 0500 START OBSERVATION : launch an OBSID to cover the basic manual commanding at the start
start_observation("FEE Checkout : FEE ON mode & system INITIALIZED state")


# 0550 system_to_initialized
# system_to_initialized() - we are executing this procedure manually, except the mechanism initialization or movements

ogse.ogse_swon()

# Success criteria : TBW

# 0560 system_test_if_initialized
system_test_if_initialized()

ogse.source_is_on()

ogse_dev: OGSEInterface = GlobalState.setup.gse.ogse.device
ogse_dev.status()
ogse_dev.operate_on()
ogse_dev.get_operate()
ogse_dev.get_lamp()
ogse_dev.get_laser()
ogse_dev.get_lamp_fault()
ogse_dev.get_controller_fault()

# The lamp and the laser are still not ON after ~10min
# ogse_dev.status() returns:
# { 'power': 'ON',
# 'lamp': 'OFF',
# 'interlock': 'OFF',
# 'psu': 'ON',
# 'att_moving': False,
# 'att_factor': 0.0,
# 'att_index': 0,
# 'power1': -9.566548e-11,
# 'temp1': 21.7,
# 'power2': 9.747926e-06,
# 'temp2': 21.6}

# Switching the OGSE OFF and restart

ogse.ogse_swoff()

ogse_dev.status()
ogse_dev.get_laser()
ogse_dev.get_lamp()
ogse_dev.get_interlock()  # CLOSED

ogse.ogse_swon()

# lamp and later still after after minutes
# We will power off and power cycle the OGSE

ogse.ogse_swoff()
ogse_dev.status()

ogse.ogse_swon()
ogse_dev.status()
ogse_dev.get_laser()
ogse_dev.get_lamp()
ogse_dev.get_operate()
ogse_dev.att_set_level_factor(factor=0)
ogse_dev.get_controller_fault()
ogse_dev.ldls_status()
ogse_dev.get_psu()
ogse_dev.get_flags()
ogse_dev.pm_status()
ogse_dev.operate_off()
ogse_dev.operate_on()

# Now the laser turned on (LED is blue)
# After a few minutes the lamp also turned on (LED turns blue)

ogse_dev.att_set_level_factor(factor=1)

ogse.ogse_swoff()  # 11:36
ogse_dev.status()
ogse.ogse_swon()  # 11:36
ogse.ogse_swoff()  # 11:37


ogse_dev.power_on()
time.sleep(5)
ogse_dev.operate_on()

system_test_if_initialized()

# 0570 : END OBSERVATION, close the obsid
end_observation()

start_observation("CAM_AAT_050 recentering: procedure test ccd 1 E")  # Observation started with obsid=CSL_00062_00120

# Nb of rows to readout
n_rows = 300

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 3.

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [1, 1, 1, 1]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = ccd_rows_pos - n_rows // 2
n_fee_parameters["row_end"] = ccd_rows_pos + n_rows // 2
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_to_dump_mode_int_sync()  # 12:06

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

dpu.n_cam_to_standby_mode()  # 12:13

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)  # 12:17

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)  # 12:21

# 0570 : END OBSERVATION, close the obsid
end_observation()

start_observation("CAM_AAT_050 recentering: procedure test ccd 1 E - take 2")  # Observation started with obsid=CSL_00062_00121

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [1, 1, 1, 1]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = ccd_rows_pos - n_rows // 2
n_fee_parameters["row_end"] = ccd_rows_pos + n_rows // 2
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

from egse.aeu.aeu import CRIOProxy

crio = CRIOProxy()
crio.get_id()

start_observation("CAM_AAT_050 recentering: dark")  # Observation started with obsid=CSL_00062_00122

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [1, 1, 1, 1]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = ccd_rows_pos - n_rows // 2
n_fee_parameters["row_end"] = ccd_rows_pos + n_rows // 2
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full image 1 E")  # Observation started with obsid=CSL_00062_00123

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [1, 1, 1, 1]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full image 2 E")  # Observation started with obsid=CSL_00062_00124

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [2, 2, 2, 2]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full 3 E")  # Observation started with obsid=CSL_00062_00125

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [3, 3, 3, 3]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full 4 E")  # Observation started with obsid=CSL_00062_00126

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [4, 4, 4, 4]
ccd_sides_pos = 'E'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full image 1 F")  # Observation started with obsid=CSL_00062_00127

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [1, 1, 1, 1]
ccd_sides_pos = 'F'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full image 2 F")  # Observation started with obsid=CSL_00062_00128

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [2, 2, 2, 2]
ccd_sides_pos = 'F'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full 3 F")  # Observation started with obsid=CSL_00062_00129

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [3, 3, 3, 3]
ccd_sides_pos = 'F'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

start_observation("CAM_AAT_050 recentering: dark full 4 F")  # Observation started with obsid=CSL_00062_00130

n_rows = 600
exposure_time = 3.
num_cycles = 5

ccd_rows_pos = 2000
ccd_codes_pos = [4, 4, 4, 4]
ccd_sides_pos = 'F'

n_fee_parameters = dict()
n_fee_parameters["num_cycles"] = num_cycles
n_fee_parameters["row_start"] = 0
n_fee_parameters["row_end"] = 4509
n_fee_parameters["rows_final_dump"] = 4510
n_fee_parameters["ccd_order"] = ccd_codes_pos
n_fee_parameters["ccd_side"] = ccd_sides_pos

print(n_fee_parameters)

dpu.n_cam_partial_int_sync(**n_fee_parameters, exposure_time=exposure_time)

end_observation()

# Lunch Time

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=300,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=3.
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # NO darks OBSID 131


n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=300,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # No dark OBSID 132

# The haxepod was moved to zero position

from egse.stages.huber.smc9300 import HuberSMC9300Proxy

huber = HuberSMC9300Proxy()
huber.info()
huber.goto(3, -36.572, False)

ogse_dev.att_set_level_factor(factor=0)
ogse_dev.status()

# 15:34

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 133

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 134

ogse_dev.att_set_level_factor(factor=1)
ogse_dev.status()

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 135

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 136

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 137

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 138

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 139

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 140

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 141

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 142

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 143

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 144

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 145

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 146

# we are here at 16:52

# We have installed the hartmann mask and covered some more disturbing lights

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 147

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 148

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 149

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=3.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 150

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=4.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 151

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=5.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 152

n_fee_parameters = dict(
    num_cycles=10,
    row_start=2500,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 153

start_observation("moving from FOV of 4 degrees to FOV at 2 degrees")
huber.goto(3, -18.264, False)
huber.goto(2, 1.0, False)
end_observation()

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 155

n_fee_parameters["exposure_time"] = 1.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 156

n_fee_parameters["exposure_time"] = 2.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 157

n_fee_parameters["exposure_time"] = 3.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 158

n_fee_parameters["exposure_time"] = 4.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 159

n_fee_parameters["exposure_time"] = 5.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 160

# one of the previous frames might be corrupt... iPhone flash

n_fee_parameters = dict(
    num_cycles=10,
    row_start=2500,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 161

start_observation("moving from FOV of 2 degrees to FOV at 6 degrees")
huber.goto(3, -54.970, False)
huber.goto(2, 3.0, False)
end_observation()

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 163

n_fee_parameters["exposure_time"] = 1.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 164

n_fee_parameters["exposure_time"] = 2.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 165

n_fee_parameters["exposure_time"] = 3.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 166

n_fee_parameters["exposure_time"] = 4.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 167

n_fee_parameters["exposure_time"] = 5.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 168

n_fee_parameters = dict(
    num_cycles=10,
    row_start=2500,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 169

start_observation("moving from FOV of 4 degrees to FOV at 2 degrees, including correction")
huber.goto(3, -62.827, False)
huber.goto(2, 3.45, False)
end_observation()

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 171

n_fee_parameters["exposure_time"] = 1.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 172

n_fee_parameters["exposure_time"] = 2.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 173

n_fee_parameters["exposure_time"] = 3.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 174

n_fee_parameters["exposure_time"] = 4.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 175

n_fee_parameters["exposure_time"] = 5.0
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 176

n_fee_parameters = dict(
    num_cycles=10,
    row_start=2500,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 177

# Retake the darks for all CCDs and 'E' and 'F'

start_observation("Attenuation factor to 0")
ogse_dev.att_set_level_factor(factor=0)
ogse_dev.status()
end_observation()

# Full frames WITH clear out

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 179

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 180

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 181

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 182

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 183

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 184

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 185

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 186

# Full frames WITHOUT clear out

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 187

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 188

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 189

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 190

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 191

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 192

n_fee_parameters = dict(
    num_cycles=10,
    row_start=0,
    row_end=4539,
    rows_final_dump=0,
    ccd_order=[4, 4, 4, 4],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 193

n_fee_parameters["ccd_side"] = 'F'
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 194


n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=499,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 195

n_fee_parameters["row_start"] = 500
n_fee_parameters["row_end"] = 999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 196

n_fee_parameters["row_start"] = 1000
n_fee_parameters["row_end"] = 1499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 197

n_fee_parameters["row_start"] = 1500
n_fee_parameters["row_end"] = 1999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 198

n_fee_parameters["row_start"] = 2000
n_fee_parameters["row_end"] = 2499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 199

n_fee_parameters["row_start"] = 2500
n_fee_parameters["row_end"] = 2999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 200

n_fee_parameters["row_start"] = 3000
n_fee_parameters["row_end"] = 3499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 201

n_fee_parameters["row_start"] = 3500
n_fee_parameters["row_end"] = 3999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 202

n_fee_parameters["row_start"] = 4000
n_fee_parameters["row_end"] = 4499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 203

n_fee_parameters["row_start"] = 4000
n_fee_parameters["row_end"] = 4539
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 204

# F-side

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=499,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 205

n_fee_parameters["row_start"] = 500
n_fee_parameters["row_end"] = 999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 206

n_fee_parameters["row_start"] = 1000
n_fee_parameters["row_end"] = 1499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 207

n_fee_parameters["row_start"] = 1500
n_fee_parameters["row_end"] = 1999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 208

n_fee_parameters["row_start"] = 2000
n_fee_parameters["row_end"] = 2499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 209

n_fee_parameters["row_start"] = 2500
n_fee_parameters["row_end"] = 2999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 210

n_fee_parameters["row_start"] = 3000
n_fee_parameters["row_end"] = 3499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 211

n_fee_parameters["row_start"] = 3500
n_fee_parameters["row_end"] = 3999
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 212

n_fee_parameters["row_start"] = 4000
n_fee_parameters["row_end"] = 4499
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 213

n_fee_parameters["row_start"] = 4000
n_fee_parameters["row_end"] = 4539
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # Yes dark OBSID 214


# Mecdhanisms were put back to zero position manually using the GUI

execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)

ogse_dev: OGSEInterface = GlobalState.setup.gse.ogse.device
ogse_dev.status()
ogse_dev.operate_off()
ogse_dev.power_off()

# 18:15 going home!
