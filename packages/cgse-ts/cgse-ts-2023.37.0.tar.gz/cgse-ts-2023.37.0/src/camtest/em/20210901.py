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

# The AEU was updated to version 1.02

crio = GlobalState.setup.gse.aeu.crio.device
crio.get_id()  # returns ('National Instruments', 'cRIO-9063', '01F0B009', 1.02)


start_observation("Switch on procedure: Test updated AEU")  # obsid=CSL_00063_00285

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

end_observation()


execute(dpu.n_cam_to_standby_mode)  # OBSID = CSL_00063_00286
execute(dpu.n_cam_to_dump_mode_int_sync)  # OBSID = CSL_00063_00287

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00288

# Executed PART OF csl_alignment_fpa_prealignment_as_run_20210901.py

start_observation("Switch off procedure: Test updated AEU")  # obsid=CSL_00063_00285

aeu.n_cam_sync_disable()
aeu.n_cam_swoff()

end_observation()


# Going home 17:17





