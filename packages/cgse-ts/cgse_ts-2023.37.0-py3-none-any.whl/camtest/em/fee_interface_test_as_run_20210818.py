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

from rich import print

from camtest import load_setup, execute
from camtest import start_observation, end_observation
### 0220 [procedure PLATO-KUL-PL-TP-0004, SWON]
### IMPORTS
from camtest.commanding import aeu
from camtest.commanding import dpu
from egse.setup import submit_setup

### 0230 [procedure PLATO-KUL-PL-TP-0004, SWON]
### LOAD THE SETUP

setup = load_setup()
print(setup)

print(setup.gse.aeu.crio.calibration)
setup.gse.aeu.crio.calibration.n_cam_uvp_s_t = [300.0, 300.0, 300.0, 300.0, 300.0, 300.0]

setup = submit_setup(setup, "increased the uvp start time to 300ms for n_cam")
setup.get_id()  # Setup 62

# Since the submit_setup doesn't update the GlobalState... yet

from camtest import GlobalState
GlobalState.load_setup()
GlobalState.setup.get_id() # Setup 62

execute(aeu.n_cam_swon)

### AEU ENABLE SYNC SIGNAL
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=1)

### N-FEE to ON MODE
### N-FEE ON, CCDs NOT POWERED

# 0510 : AEU SWON puts the FEEs in on mode --> is_on_mode should return True already
dpu.n_cam_is_on_mode()

# 0500 START OBSERVATION : launch an OBSID to cover the basic manual commanding at the start
start_observation("FEE Checkout : FEE ON mode & system INITIALIZED state")
# 2021-08-18 11:44:07,943:         MainProcess:    INFO:  349:camtest.core.exec   :Observation started with obsid=CSL_00058_00104
# Active Setup is still 62 however. This is a problem of propagating the updated Setup to the Storage manager

# 0520 : go to on mode
dpu.n_cam_to_on_mode()

# 0530 : is_on_mode should return True
dpu.n_cam_is_on_mode()

end_observation()

start_observation("FEE Checkout : FEE Pattern mode")
# 2021-08-18 12:39:05,017:         MainProcess:    INFO:  349:camtest.core.exec   :Observation started with obsid=CSL_00058_00105

from egse.dpu import DPUProxy
dpu = DPUProxy()

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=1,
)
print(f"{n_fee_parameters=}")
dpu.n_fee_set_full_image_pattern_mode(n_fee_parameters)

#2021-08-18 12:41:09,047:       dpu.processor:   ERROR: 1557:egse.dpu            :Exception during command execution in DPU Processor: <function command_set_full_image_pattern_mode at 0x7f258f52f940>
#Traceback (most recent call last):
#  File "/cgse/lib/python/Common_EGSE-2021.3rc21-py3.8.egg/egse/dpu/__init__.py", line 1544, in send_commands_to_n_fee
#    response = command(transport, register_map, *args)
#TypeError: command_set_full_image_pattern_mode() takes from 2 to 4 positional arguments but 5 were given


dpu.n_fee_set_on_mode()

end_observation()

# !!!! System crashed, flickering screen, had to power cycle the egse-client-2

# After lunch had to restart the egse-client again -> flickering screen
# 14:14 I updated the egse-server to 2021.3-RC22 and restarted the dpu_cs
#       re-imported the modules and functions from the top
#       re-loaded the Setup -> 62
#       re-loaded the GlobalState
#       core services and AEU_CS not touched

start_observation("FEE Checkout : FEE Pattern mode - take 2")
# 2021-08-18 14:18:42,917:         MainProcess:    INFO:  349:camtest.core.exec   :Observation started with obsid=CSL_00058_00106

from egse.dpu import DPUProxy
dpu = DPUProxy()

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=1,
)
print(f"{n_fee_parameters=}")
dpu.n_fee_set_full_image_pattern_mode(n_fee_parameters)

dpu.n_fee_set_on_mode()

dpu.n_fee_get_full_register()

end_observation()


execute(aeu.n_cam_is_syncing)
execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)

execute(aeu.n_cam_swon)

execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)

from egse.dpu import DPUProxy
dpu = DPUProxy()


n_fee_parameters = dict(
    int_sync_period=6250
)
print(f"{n_fee_parameters=}")
dpu.n_fee_set_internal_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=1,
)
print(f"{n_fee_parameters=}")
dpu.n_fee_set_full_image_pattern_mode(n_fee_parameters)
dpu.n_fee_set_on_mode()

dpu.n_fee_set_external_sync({})

dpu.n_fee_set_full_image_pattern_mode(n_fee_parameters)

execute(aeu.get_n_cam_sync_status)

reg = dpu.n_fee_get_full_register()
print(reg)

n_fee_parameters = dict(
    int_sync_period=6250
)
print(f"{n_fee_parameters=}")
dpu.n_fee_set_internal_sync(n_fee_parameters)

reg = dpu.n_fee_get_full_register()
print(reg)

dpu.n_fee_set_standby_mode()

n_fee_parameters = dict(
    v_start=0,
    v_end=499,
    sensor_sel=1,
    num_cycles=10,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

# Started FITS generation

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=1,
    num_cycles=10,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=500,
    sensor_sel=3,
    num_cycles=10,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=3,
    num_cycles=10,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=3,
    num_cycles=10,
    ccd_readout_order=0b01100100,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=3,
    num_cycles=10,
    ccd_readout_order=0b01010101,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=3,
    num_cycles=10,
    ccd_readout_order=0b10101010,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

n_fee_parameters = dict(
    v_start=0,
    v_end=4509,
    sensor_sel=3,
    num_cycles=10,
    ccd_readout_order=0b11111111,
)
print(f"{n_fee_parameters=}")

dpu.n_fee_set_full_image_mode_int_sync(n_fee_parameters)

dpu.n_fee_set_standby_mode()
dpu.n_fee_set_on_mode()

execute(aeu.n_cam_is_syncing)
execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)
