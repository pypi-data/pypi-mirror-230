from camtest import start_observation, end_observation
from camtest.commanding import dpu
from camtest.commanding import system_to_idle, system_test_if_idle, system_to_initialized, system_test_if_initialized
from egse.exceptions import Abort

start_observation("FEE Checkout :  FEE ON mode")

if not dpu.n_cam_is_on_mode():

    raise Abort("N-FEE should go to on mode when the AEU is switched on")

dpu.n_cam_to_on_mode()

if not dpu.n_cam_is_on_mode():

    raise Abort("Putting the N-FEE in on mode did not succeed")

# Success criteria : check in DPU_UI

end_observation()


### SYSTEM TO INITIALIZED STATE

start_observation("System INITIALIZED state")

system_to_initialized()

system_test_if_initialized()

end_observation()


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


