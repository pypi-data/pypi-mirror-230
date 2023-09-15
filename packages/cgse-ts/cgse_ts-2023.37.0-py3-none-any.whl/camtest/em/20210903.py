import time

from rich import print

from camtest import execute
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.csl_gse import csl_point_source_to_fov
from egse.dpu import DPUProxy
from egse.hexapod.symetrie.puna import PunaProxy

is_model_sync(model, hexhw)

execute(ogse.ogse_swon)

execute(ogse.ogse_set_attenuation_level, fwc_fraction=1.0)
ogse.att_get_factor()

execute(csl_point_source_to_fov, theta=8.3, phi=153.0, wait=False)

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)

# Forgot to switch on the N-CAM -> DPU (and fitsgen) crashed

execute(aeu.n_cam_swon)
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)

# DPU revived automatically
# FITS generator needed to be re-started

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 334

# Should have gone to stand-by mode first
# AI: Check whether we're in stand-by mode when we go to internal sync

execute(dpu.n_cam_to_standby_mode)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 336

# For this obsid the lights were still on

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 337

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 338

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.8)      # obsid: 339
ogse.att_get_factor()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 340

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=3.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 341

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.6)      # obsid: 342
ogse.att_get_factor()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=3.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 343

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=6.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 344

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.55)      # obsid: 345
ogse.att_get_factor()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=6.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 346

# Potentially didn't wait long enough to reach the attenuation level

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 347

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.48)      # obsid: 348
ogse.att_get_factor()
ogse_proxy.status()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=6.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 349


execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.35)      # obsid: 350
ogse.att_get_factor()
ogse_proxy.status()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=12.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 351

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.33)      # obsid: 352
ogse.att_get_factor()
time.sleep(1)
ogse_proxy.status()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=12.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 353

# Cannot find back the source now

# Moving the hexapod

print(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("toul6")))
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

# Move the hexapod

vtrans = [0, 0, 3.]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

vtrans = [0, 0, 2.]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

print(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")))

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

print(model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")))


execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.33)      # obsid: 358
ogse.att_get_factor()
time.sleep(1)
ogse.att_is_moving()

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 359

model.hexapod_goto_retracted_position()

execute(hexapod_puna_goto_retracted_position, wait=True)

is_model_sync(model, hexhw)

print(model.get_frame("toul6").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann")))
print(model.get_frame("toul6").getActiveTranslationRotationVectorsTo(model.get_frame("toubip")))


model.hexapod_goto_zero_position()
execute(hexapod_puna_goto_zero_position, wait=True)
is_model_sync(model, hexhw)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 0]
vrot = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [0, 0, 5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [0, 0, 5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


# CCD connector sticking out: are we sure that it will not collide with L6 before reaching the position?
# (The avoidance volume is based on the mask and L6)

puna_proxy = PunaProxy()
puna_proxy.get_speed()  # Translation speed v_t [mm/s], Rotation speed v_r [degrees/s], v_t_min, v_r_min, v_t_max, v_r_max

# At this point, the speeds are: [2.0, 1.0, 0.01, 0.001, 4.0, 2.0]
# Reduce the translation speed to 0.1mm/s (keep the same speed for the rotation)

puna_proxy.set_speed(0.1, 1.0)
puna_proxy.get_speed()


ogse.att_get_factor()

execute(dpu.n_cam_to_on_mode)
execute(dpu.n_cam_to_standby_mode)

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 370


execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.35)      # obsid: 371
print(ogse.att_get_factor())
time.sleep(1)
print(ogse.att_is_moving())

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=3.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 372

execute(ogse.ogse_set_attenuation_level, fwc_fraction=0.8)      # obsid: 373
print(ogse.att_get_factor())
time.sleep(2)
print(ogse.att_is_moving())

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 374


# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 1.0

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

####################################################
# BUILDING BLOCK EXECUTION
####################################################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 375

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 1]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 377


vtrans = [0, 0, 1]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 379

# 6mm away from the Hartmann plane

exposure_time = 0.5
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 380

vtrans = [0, 0, 3]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)

# 3mm away from the Hartmann plane (fully re-centered)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 383

# 3mm away from the Hartmann plane (fully re-centered)

exposure_time = 0.2
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 384

# The server crashed

execute(aeu.n_cam_swon)
execute(aeu.n_cam_sync_enable, image_cycle_time=25, svm_nom=1, svm_red=0)

execute(dpu.n_cam_to_on_mode)
execute(dpu.n_cam_to_standby_mode)

dpu_proxy = DPUProxy()
dpu_proxy.n_fee_set_internal_sync({})
execute(dpu.n_cam_to_dump_mode_int_sync)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.2
)

# 3mm away from the Hartmann plane (fully re-centered)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 391

exposure_time = 0.2
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 392

vtrans = [0, 0, 1]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)

# 2mm away from the Hartmann plane

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 394

vtrans = [0, 0, 0.5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)

# 1.5mm away from the Hartmann plane

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 396

vtrans = [0, 0, -0.25]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)


# 1.75mm away from the Hartmann plane

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 398

vtrans = [0, 0, 0.75]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)


# 1mm away from the Hartmann plane

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 400

exposure_time = 0.2
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 401



vtrans = [0, 0, 0.5063]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


# Exactly at 0.5mm away from the Hartmann plane

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)     # obsid: 403

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

# [[ 0.0008  0.0038  0.5   ]
#  [-0.      0.      0.    ]]

vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])


vtrans = [0, 0, 0.5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

exposure_time = 0.2
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 406


vtrans = [0, 0, -0.5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])
# [[ 0.  -0.   0.5]
#  [ 0.  -0.  -0. ]]

exposure_time = 0.2
execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)   # obsid: 408

# Move back to the Hartmann plane and register the model in the setup

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [0, 0, 0.5]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

vtrans = [trans[0], trans[1], 0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartmann"))
printm([trans, rot])

csl_dict = model.serialize()
setup.csl_model.model = csl_dict
setup = submit_setup(setup, "CSLReferenceFrameModel EM 003 20210903 EOB - FPA on Hartmann plane")


execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)
execute(ogse.ogse_swoff)

# Stop DPU CS
# Stop FITS generator

# Weekend!! :)
