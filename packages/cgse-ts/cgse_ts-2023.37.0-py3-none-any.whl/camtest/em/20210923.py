import logging
import os

from rich import print

from camtest import GlobalState
from camtest import end_observation
from camtest import execute
from camtest import load_setup
from camtest import start_observation
from camtest.analysis.convenience import printm
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.commanding.csl_gse import is_model_sync
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry
from camtest.commanding.functions.fov_test_geometry import fov_geometry_from_table
from camtest.commanding.functions.fov_test_geometry import sort_on_azimuth
from egse.settings import Settings
from egse.setup import submit_setup

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

rot_config = "sxyz"

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")

time_step = 1.

verbose = True


# LOAD SETUP ---------------------------------------------------------------------------------------

setup = load_setup()
print(setup)  # Setup 80

GlobalState.load_setup()
GlobalState.setup.get_id()

# We used the same Python Console as yesterday, meaning the model is still valid!!!!!!!!!!!!!!!!!!!!
# SYSTEM SWITCH ON ---------------------------------------------------------------------------------

start_observation("Switch on procedure: AEU and N-FEE to STANDBY, then DUMP mode internal sync")  # obsid = CSL_00080_00591

# We had trouble with the AEU where the cRIO lost Socket connection several times and AWG-2 also stopped.
# After two reboots/power cycles we could start the AEU, switch on the camera and configure it to internal sync.
# Now we are not dependent anymore on the AWG and only need PSU to work with the N-FEE.

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

# On the server: dpu_cs start
# On the server: fitsgen start
# On the server: python -m egse.fee.n_fee_hk -platform offscreen

# On the client: dpu_ui

execute(dpu.n_cam_to_standby_mode)

# Wait until in standby mode

print(dpu.n_cam_is_standby_mode())

execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())



start_observation("Switch on procedure: OGSE")  # obsid = CSL_00080_00592

ogse.ogse_swon()
ogse.set_fwc_fraction(fwc_fraction=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()

end_observation()


# PERFORM THE '8-DEG CIRCLE' as a reference measurement --------------------------------------------


# Test position - test image to confirm everything is alright

execute(csl_point_source_to_fov,
        theta=8.3, phi=-153.0, wait=False, theta_correction=False, sma_correction=False)  # obsid = CSL_00080_00593

n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2, 2, 2, 2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # obsid = CSL_00080_00594 and CSL_00080_00596


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE -------------------------------------------------

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(
    anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

sma_correction = False
theta_correction = False


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00597


# Load the model and check if in sync with Hexapod -------------------------------------------------

# hexhw = PunaProxy()
#
# setupmodel = setup.csl_model.model
# model = CSLReferenceFrameModel(setupmodel)
# print(model.summary())
#
# is_model_sync(model, hexhw)


# Check if we are on Hartmann plane ----------------------------------------------------------------

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])

vtrans = [0, 0, -0.065]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE -------------------------------------------------

boresight_angle = 8.3
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(
    anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

sma_correction = False
theta_correction = False


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00600





# FULL HARTMANN VERIFICATION -----------------------------------------------------------------------

# 'PRE-UNDOING' THE OPTICAL DISTORTION (i.e. avoid to incl. it twice in the meas wrt LDO)

distorted = True
distorted_input = True
verbose = True

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted, distorted_input=distorted_input, verbose=verbose)

angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=False)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00603

# OBSID 601 aborted due to BR rotating always in the same direction
# OBSID 602 crashed because of a lost connection with the HUBER stages
# 2021-09-23 10:11:19,900:         MainProcess:    INFO:  211:camtest.core.exec   :n_cam_to_dump_mode_int_sync({})
# 2021-09-23 10:11:20,109:         MainProcess:    INFO:  211:camtest.core.exec   :csl_point_source_to_fov({'theta': 16.258985244955742, 'phi': -56.66447176032807, 'wait': True, 'theta_correction': False, 'sma_correction': False})
# 2021-09-23 10:11:20,111:         MainProcess:    INFO:  211:camtest.core.exec   :rotation_stage_move({'angle': 56.66447176032807})
# 2021-09-23 10:11:20,121:         MainProcess:    INFO:  211:camtest.core.exec   :sma_rotation_move({'angle': 8.188870436592449})
# 2021-09-23 10:11:20,125:         MainProcess:    INFO:  211:camtest.core.exec   :sma_translation_move({'distance': -152.52958845463993})
# 2021-09-23 10:11:21,126:         MainProcess:CRITICAL:  240:HuberSMC9300Proxy   :Control Server seems to be off-line, abandoning
# 2021-09-23 10:11:21,126:         MainProcess: WARNING:  125:HuberSMC9300Proxy   :HuberSMC9300Proxy could not connect to its control server at tcp://139.165.177.74:6800. No commands have been loaded.
# Traceback (most recent call last):
#   File "/cgse/lib/python/ipython-7.26.0-py3.8.egg/IPython/core/interactiveshell.py", line 3441, in run_code
#     exec(code_obj, self.user_global_ns, self.user_ns)
#   File "<ipython-input-107-715ac885c20d>", line 1, in <module>
#     execute(cam_aat_050_ambient_recentering,
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/core/exec.py", line 313, in execute
#     response = func(*args, **kwargs)
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/core/exec.py", line 237, in wrapper_func
#     result = func(*args, **kwargs)
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/commanding/cam_aat_050_ambient_recentering.py", line 66, in cam_aat_050_ambient_recentering
#     csl_point_source_to_fov(theta=theta, phi=phi, wait=True, theta_correction=theta_correction, sma_correction=sma_correction)
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/core/exec.py", line 237, in wrapper_func
#     result = func(*args, **kwargs)
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/commanding/csl_gse.py", line 637, in csl_point_source_to_fov
#     sma_translation_move(distance=-(delta_x - offset_delta_x))
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/core/exec.py", line 237, in wrapper_func
#     result = func(*args, **kwargs)
#   File "/home/plato-data/git/plato-test-scripts/src/camtest/commanding/csl_gse.py", line 165, in sma_translation_move
#     stages.goto(STAGES_SETTINGS.TRANSLATION_STAGE, distance, False)
#   File "/home/plato-data/git/plato-common-egse/src/egse/stages/huber/smc9300.py", line 86, in goto
#     raise NotImplementedError
# NotImplementedError



# Introducing NEWLDO Reference Frame -----------------------------------------------------------------------------------

transhart = model.get_frame('toumec').getActiveTranslationVectorTo(model.get_frame('hartmann'))
transhart[2] -= 0.065
model.add_frame(name="newldo", translation=transhart, rotation=[-0.0145,-0.034,0], ref='hartflat')
model.add_link("newldo", "hartflat")
printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("newldo")))

trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])

# NEWLDO was ill defined, removing the reference frame and creating a new one ------------------------------------------

model.remove_frame('newldo')

model.add_frame(name="newldo", translation=[0,0,-0.065], rotation=[-0.0145,-0.034,0], ref='hartflat')
model.add_link("newldo", "hartflat")
printm(model.get_frame("toumec").getActiveTranslationRotationVectorsTo(model.get_frame("newldo")))
# [[ 0.0000e+00 -1.0000e-04 -6.8127e+01]
#  [-6.9500e-02 -4.3000e-02  1.2200e-02]]
printm(model.get_frame("hartmann").getActiveTranslationRotationVectorsTo(model.get_frame("newldo")))
# [[0.0002 - 0.0004 - 0.065]
#  [0.0179 - 0.0617 - 0.0001]]
printm(model.get_frame("hartflat").getActiveTranslationRotationVectorsTo(model.get_frame("newldo")))
# [[ 0.     -0.     -0.065 ]
#  [-0.0145 -0.034   0.    ]]

trans, rot = model.get_frame("hartflat").getActiveTranslationRotationVectorsTo(model.get_frame("newldo"))
printm([trans, rot])

vtrans = trans
vrot = rot

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)


trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("newldo"))
printm([trans, rot])
trans, rot = model.get_frame("fpasen").getActiveTranslationRotationVectorsTo(model.get_frame("hartflat"))
printm([trans, rot])

vtrans = [0, 0, 0.065]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
# Hexapod   : [-2.229e-01 -2.900e-03 -3.514e+00 -6.950e-02 -4.300e-02  1.220e-02]
# Model     : [-2.229e-01 -2.800e-03 -3.514e+00 -6.950e-02 -4.300e-02  1.220e-02]
# Diff      : [ 0.     -0.0001  0.      0.      0.      0.    ]
# In synch  : True




# COMPUTATION FOV & CCD COORDINATES FOR THE CIRCLE -------------------------------------------------

boresight_angle = 12.4
n_pos = 20

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(
    anglesorig, [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig], reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
for c, (angle, crow, ccol, ccode, ccd_side) in enumerate(zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides)):
    print(f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")


# Nb of rows to readout
width = 1500
# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2
# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

sma_correction = False
theta_correction = False


execute(cam_aat_050_ambient_recentering,
        num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides,
        n_rows=width, theta_correction=theta_correction, sma_correction=sma_correction)  # obsid = CSL_00080_00606 - 11:25

# Saving the model

csl_dict = model.serialize()

setup.csl_model.model =  csl_dict
setup = submit_setup(setup,"CSLReferenceFrameModel EM 005 - at fpasen = hartflat - 0.065")  # Setup 82
setup = load_setup()
print(setup)

# Ann is taking over to measure the TOU_MEC with LTT -------------------------------------------------------------------

# Moved big rotation stage to 59.8246 degC
# Moved FPA down in several movements: z = -1, -2, -2, -5, -5 = -15mm in total

vtrans = [0, 0, -5.0]
vrot = [0, 0, 0]

move_ok = execute(check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup, verbose=verbose)

is_model_sync(model, hexhw)
# Hexapod   : [-2.2300e-01 -2.9000e-03 -1.8514e+01 -6.9500e-02 -4.3000e-02  1.2200e-02]
# Model     : [-2.2290e-01 -2.8000e-03 -1.8514e+01 -6.9500e-02 -4.3000e-02  1.2200e-02]
# Diff      : [-0.0001 -0.0001  0.      0.      0.     -0.    ]
# In synch  : True

# LUNCH TIME -----------------------------------------------------------------------------------------------------------




# SYSTEM SWITCH OFF --------------------------------------------------------------------------------

start_observation("Switch OFF: OGSE")

# aeu.n_cam_sync_disable()
# aeu.n_cam_swoff()
ogse.ogse_swoff()

end_observation()
