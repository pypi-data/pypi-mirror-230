from rich import print

from camtest import load_setup, execute
from camtest import GlobalState
from camtest import start_observation, end_observation

from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from egse.collimator.fcul.ogse import OGSEProxy
from egse.stages.huber.smc9300 import HuberSMC9300Proxy
from camtest.commanding.csl_gse import csl_point_source_to_fov
from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.csl_gse import csl_point_source_to_fov
from egse.collimator.fcul.ogse import OGSEProxy
from egse.stages.huber.smc9300 import HuberSMC9300Proxy

setup = load_setup()
print(setup)  # Setup 63

GlobalState.load_setup()
GlobalState.setup.get_id() # Setup 63

start_observation("Switch on procedure")  # obsid=CSL_00063_00230

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

# Started the DPU CS

dpu.n_cam_to_dump_mode_int_sync()

ogse.ogse_swon()

# Check the status of the OGSE

ogse_proxy = OGSEProxy()
ogse_proxy.status()

end_observation()

start_observation("Set attenuation to factor=1")  # obsid=CSL_00063_00231

# We don't have a camtest command to set the OGSE attenuation

ogse_proxy.att_set_level_factor(factor=1)

end_observation()


TRANS = 3
SMALL_ROT = 2
BIG_ROT = 1
huber = HuberSMC9300Proxy()
huber.info()

start_observation("Moving the translation stage")  # obsid=CSL_00063_00232
huber.goto(TRANS, -54.970, False)
huber.goto(SMALL_ROT, +3, False)
end_observation()


n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00233

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00234

execute(dpu.n_cam_to_standby_mode)  # OBSID = CSL_00063_00235

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00236

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=1.0
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00237

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00238


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

# We saw the source in CCD 3 F, but it was displayed in CCD 1 left side!

# Traceback (most recent call last):
#   File "/cgse/lib/python/Common_EGSE-2021.3rc28-py3.8.egg/egse/dpu/dpu_ui.py", line 240, in worker_output
#     self.image.add_data(data_packet)
#   File "/cgse/lib/python/Common_EGSE-2021.3rc28-py3.8.egg/egse/dpu/ccd_ui.py", line 56, in add_data
#     self.image_E[self.index_E:self.index_E+data_length] = data
# ValueError: could not broadcast input array from shape (16065,) into shape (9180,)

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00247 - fully saturated

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00248 - fully saturated

# Started FITSGEN  11:22


n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00249

# FITSGEN failed
# Traceback (most recent call last):
#   File "/cgse/bin/fitsgen", line 11, in <module>
#     load_entry_point('Common-EGSE==2021.3rc28', 'console_scripts', 'fitsgen')()
#   File "/cgse/lib/python/click-8.0.0a1-py3.8.egg/click/core.py", line 1025, in __call__
#     return self.main(*args, **kwargs)
#   File "/cgse/lib/python/click-8.0.0a1-py3.8.egg/click/core.py", line 955, in main
#     rv = self.invoke(ctx)
#   File "/cgse/lib/python/click-8.0.0a1-py3.8.egg/click/core.py", line 1517, in invoke
#     return _process_result(sub_ctx.command.invoke(sub_ctx))
#   File "/cgse/lib/python/click-8.0.0a1-py3.8.egg/click/core.py", line 1279, in invoke
#     return ctx.invoke(self.callback, **ctx.params)
#   File "/cgse/lib/python/click-8.0.0a1-py3.8.egg/click/core.py", line 710, in invoke
#     return callback(*args, **kwargs)
#   File "/cgse/lib/python/Common_EGSE-2021.3rc28-py3.8.egg/egse/dpu/fitsgen.py", line 664, in start
#     fg.run()
#   File "/cgse/lib/python/Common_EGSE-2021.3rc28-py3.8.egg/egse/dpu/fitsgen.py", line 162, in run
#     ccd_readout_order = convert_ccd_order_value(ccd_readout_order)
# UnboundLocalError: local variable 'ccd_readout_order' referenced before assignment

# FITSGEN fixed in 2021.3-RC29

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00250

start_observation("Resetting BIG rotation stage - zero point")  # obsid=CSL_00063_00251
huber.goto(BIG_ROT, -59.825647, False)

# gse.control.Failure('Executing goto failed: ',
#                      ModuleNotFoundError("No module named 'egse.confman'"))

end_observation()

# The above error comes from updating the CGSE on the server, but not restarting the system
# Restarted the system now
#  * stopped all CS on the server
#  * restarted the core services
#  * restarted all the device CS

start_observation("Resetting BIG rotation stage - zero point - take 2")  # obsid=CSL_00063_00252
huber.goto(BIG_ROT, -59.825647, False)
huber.zero(BIG_ROT)
end_observation()

# Trying to clear out the convention


execute(csl_point_source_to_fov, theta=6.0, phi=-63.0, wait=False)  # OBSID = CSL_00063_00253

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],  # should be CCD 3
    ccd_side="F",  # should be side E
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00254

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00255

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00256

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00257

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00258

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00259


n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00260

# run again to check ccd_order and ccd_side in DPU GUI

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00261

# run again to check FITS generation

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00262

execute(csl_point_source_to_fov, theta=14.0, phi=-27.0, wait=False)  # OBSID = CSL_00063_00263

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3, 3, 3, 3],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00264

execute(csl_point_source_to_fov, theta=14.0, phi=-99.0, wait=False)  # OBSID = CSL_00063_00265

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00266

execute(csl_point_source_to_fov, theta=6.0, phi=-99.0, wait=False)  # OBSID = CSL_00063_00267

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00268

execute(csl_point_source_to_fov, theta=6.0, phi=+9.0, wait=False)  # OBSID = CSL_00063_00269

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00270

execute(csl_point_source_to_fov, theta=14.0, phi=+9.0, wait=False)  # OBSID = CSL_00063_00271

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00272

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00273

execute(csl_point_source_to_fov, theta=14.0, phi=81.0, wait=False)  # OBSID = CSL_00063_00274

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[4, 4, 4, 4],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00275

execute(csl_point_source_to_fov, theta=14.0, phi=153.0, wait=False)  # OBSID = CSL_00063_00276

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="F",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00277

execute(csl_point_source_to_fov, theta=14.0, phi=117.0, wait=False)  # OBSID = CSL_00063_00278

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.5
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_00063_00279

# Bring back the big rotation stage to a position
huber.goto(BIG_ROT, 300, False)

# Execute the recentering script - OBSID = CSL_00063_00282

huber.goto(BIG_ROT, 150, False)

# Execute the recentering script - OBSID = CSL_00063_00283
# width = 10000 to take full images

execute(csl_point_source_to_fov, theta=0.0, phi=0.0, wait=False)  # OBSID = CSL_00063_00284

# Going home 16:41
