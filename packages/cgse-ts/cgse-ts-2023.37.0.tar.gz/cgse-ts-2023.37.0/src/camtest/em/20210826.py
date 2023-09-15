from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest.commanding import aeu
from camtest.commanding import dpu

setup = load_setup()
print(setup)  # Setup 63

GlobalState.load_setup()
GlobalState.setup.get_id() # Setup 63

aeu.get_n_cam_sync_quality()
aeu.get_n_cam_sync_quality()
aeu.get_n_cam_sync_status()
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)
aeu.n_cam_swon()  # this didn't work
aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)
aeu.get_n_cam_sync_status()  # (1, 1)
aeu.get_n_cam_sync_quality()  # (0, 0)

start_observation("AEU Checkout: external sync")

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=499,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side="F",
)

dpu.n_cam_partial_ccd(**n_fee_parameters)

end_observation()

execute(aeu.n_cam_sync_disable)

execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)

from egse.dpu import DPUProxy

dpu = DPUProxy()
dpu.n_fee_set_on_mode()

n_fee_parameters = dict(
    num_cycles=0,
    row_start=0,
    row_end=4509,
    rows_final_dump=0,
    ccd_order=[1, 2, 3, 4],
    ccd_side="BOTH",
)


dpu.n_fee_set_full_image_pattern_mode(n_fee_parameters)
dpu.n_fee_set_on_mode()

# it was not a good idea to call the proxy 'dpu', see later where I called it dpu_proxy

from camtest.commanding import dpu

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=499,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID 221

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID 222

execute(dpu.n_cam_to_standby_mode)  # OBSID 223

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=499,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID 224

execute(dpu.n_cam_to_standby_mode)  # OBSID 225

dpu_proxy = DPUProxy()

n_fee_parameters = dict(
)


dpu_proxy.n_fee_set_external_sync(n_fee_parameters)

register = dpu_proxy.n_fee_get_full_register()

execute(dpu.n_cam_to_standby_mode)  # OBSID 226
execute(dpu.n_cam_to_on_mode)  # OBSID 227

execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)

# -eof-