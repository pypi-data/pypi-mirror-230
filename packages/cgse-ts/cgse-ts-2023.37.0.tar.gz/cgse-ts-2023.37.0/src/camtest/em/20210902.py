from egse.stages.huber.smc9300 import HuberSMC9300Proxy

# Alex asked to move the big rotation stage to the following position

smc = HuberSMC9300Proxy()
smc.goto(1, 54.82565, False)  # This moved the Stage in the wrong direction
# Set back to zero position using the GUI
smc.move(1, 54.82565, False)  # This move in the right direction

from rich import print

from camtest import load_setup, execute
from camtest import GlobalState
from camtest import start_observation, end_observation

from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from egse.collimator.fcul.ogse import OGSEProxy
from camtest.commanding.csl_gse import csl_point_source_to_fov

setup = load_setup()
print(setup)  # Setup 63

GlobalState.load_setup()
GlobalState.setup.get_id()  # Setup 65

start_observation("Switch on procedure: AEU and N-FEE to STANDBY")  # obsid=CSL_00065_00290

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

dpu.n_cam_to_standby_mode()

end_observation()

execute(dpu.n_cam_to_dump_mode_int_sync)  # OBSID = CSL_00065_00291

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00292

execute(dpu.n_cam_to_standby_mode)  # OBSID = CSL_00065_00293

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00294

# Check FITS Generation

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00295

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00296

# Executing csl_alignment_fpa_prealignment...20210902.py

execute(ogse.ogse_swon)


n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00300

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00301

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00302

# Previous statemenet gave an error and left the N-FEE in an inconsistent state

execute(dpu.n_cam_to_dump_mode_int_sync)  # OBSID = CSL_00065_00303

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00304

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00305

execute(dpu.n_cam_to_dump_mode_int_sync)  # OBSID = CSL_00065_00306

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00307

# E-F side problem solved for expected versus actual last packet flags  15:04

ogse_proxy = OGSEProxy()
ogse_proxy.status()
ogse_proxy.att_set_level_factor(factor=1)


execute(csl_point_source_to_fov, theta=8.3, phi=-171.0, wait=False)  # OBSID = CSL_00065_00308

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00309

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_0030

# Running the cam_aat_050_ambient_recentering{_prep}.py  last OBSID 00311

execute(csl_point_source_to_fov, theta=8.3, phi=153.0, wait=False)  # OBSID = CSL_00065_00312

n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00313

n_fee_parameters = dict(
    num_cycles=3,
    row_start=2750,
    row_end=4250,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00314

# Running the cam_aat_050_ambient_recentering{_prep}.py  last OBSID 00315

# Continu prealignment

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans,rot],6)

vtrans = [0, 0, 5]
vrot   = [0, 0, 0]

is_model_sync(model, hexhw)

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

print(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00317

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00318

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00319

ogse_proxy.att_set_level_factor(factor=0.35)
ogse_proxy.status()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00320

ogse_proxy.att_set_level_factor(factor=0.8)
ogse_proxy.status()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00321

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=2.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00065_00322

# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 3.0

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)

# ObsID 323

execute(ogse.ogse_swoff)  # OBSID = CSL_00065_00324
execute(aeu.n_cam_sync_disable)  # OBSID = CSL_00065_00325
execute(aeu.n_cam_swoff)  # OBSID = CSL_00065_00326






n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

for ccd in [1, 2, 3, 4]:  # OBSID = CSL_00063_00239 -> CSL_00063_00246
    for side in ['E', 'F']:
        n_fee_parameters["ccd_order"] = [ccd, ccd, ccd, ccd]
        n_fee_parameters["ccd_side"] = side
        execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)


