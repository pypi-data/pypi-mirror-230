import logging
import os

import numpy as np
from rich import print

from camtest import GlobalState
from camtest import load_setup, execute
from camtest import start_observation, end_observation
from camtest.commanding import aeu
from camtest.commanding import dpu
from camtest.commanding import ogse
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.csl_gse import csl_point_source_to_fov
from camtest.commanding.functions.fov_test_geometry import angles_to_ccd_coordinates
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.hexapod.symetrie.puna import HexapodError
from egse.hexapod.symetrie.puna import PunaProxy
# Hexapod
from egse.hexapod.symetrie.puna import PunaSimulator
from egse.settings import Settings


# from egse.coordinates.avoidance import is_avoidance_ok
# Scripts


# Convenience functions
def printm(matrix, rounding=4):
    print(np.round(matrix, rounding))


def positions_match(hexapod, hexsim, atol=0.0001, rtol=0.0001):
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)


def is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    if verbose is None: verbose = ""

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(model.get_frame('hexobj'))
    coomod = np.concatenate([coomodtr, coomodrot])

    print(f"{verbose}Hexapod   : {np.round(coohex, rounding)}")
    print(f"{verbose}Model     : {np.round(coomod, rounding)}")
    print(f"{verbose}Diff      : {np.round(coohex - coomod, rounding)}")

    print(f"{verbose}In synch  : {np.allclose(coohex, coomod, atol=atol, rtol=rtol)}")

    return


def hex_positions(hexapod, rounding=3):
    """
    Print User and machine coordinates of the input Hexapod

    Parameters
    ----------
    hexapod : Hexapod

    Returns
    -------
    None

    """
    print(f"OBJ vs USR: {np.round(hexapod.get_user_positions(), rounding)}")
    print(f"PLT vs MEC: {np.round(hexapod.get_machine_positions(), rounding)}")
    return


rot_config = "sxyz"

confdir = os.getenv("PLATO_CONF_DATA_LOCATION")

time_step = 1.

setup = load_setup()
print(setup)  # Setup 63

GlobalState.load_setup()
GlobalState.setup.get_id()  # Setup 65

start_observation("Switch on procedure: AEU and N-FEE to STANDBY")  # obsid=CSL_00065_00290

aeu.n_cam_swon()
aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)


# On the server : dpu_cs start
dpu.n_cam_to_standby_mode()

end_observation()


execute(dpu.n_cam_to_dump_mode_int_sync)

execute(ogse.ogse_swon)
execute(ogse.set_relative_intensity, relative_intensity=0.8)

# ogse.att_get_factor()
ogse.get_relative_intensity()
# ogse.att_is_ready()
ogse.attenuator_is_ready()

# ogse_proxy = OGSEProxy()
# ogse_proxy.status()
# ogse_proxy.att_set_level_factor(factor=1)

# $fitsgen start

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1, 1, 1, 1],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)

print(model.summary())


try:
    #hexhw = PunaController()
    #hexhw.connect()
    hexhw  = PunaProxy()
    hexhw.info()
except HexapodError:
   hexhw = PunaSimulator()
except NotImplementedError:
   hexhw = PunaSimulator()

print(f"Hexapod HW is simulator: {hexhw.is_simulator()}")

is_model_sync(model, hexhw)

printm(model.get_frame('fpasen').getActiveTranslationRotationVectorsTo(model.get_frame('hartmann')))

n_fee_parameters = dict(
    num_cycles=3,
    row_start=1750,
    row_end=3250,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 419

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[1,1,1,1],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 420


execute(csl_point_source_to_fov, theta=3.1, phi=-153.0, wait=True) # obsid 421


n_fee_parameters = dict(
    num_cycles=3,
    row_start=2000,
    row_end=3500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 422

n_fee_parameters = dict(
    num_cycles=3,
    row_start=3000,
    row_end=4500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 423

# Recentering obs a 3.1
#######################
# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) # obsid 424


execute(csl_point_source_to_fov, theta=12.4, phi=-153.0, wait=True) # obsid 425


n_fee_parameters = dict(
    num_cycles=3,
    row_start=1000,
    row_end=2500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 426


# Recentering obs a 12.4
#######################
# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) # obsid 427

execute(csl_point_source_to_fov, theta=16.33, phi=-153.0, wait=True) # obsid 428


n_fee_parameters = dict(
    num_cycles=3,
    row_start=0,
    row_end=1500,
    rows_final_dump=4510,
    ccd_order=[2,2,2,2],
    ccd_side="E",
    exposure_time=0.2
)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters) # obsid 429

# Recentering obs a 16.33
#########################

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) # obsid 430


## START SMA MISALIGNMENT CHECK -- OBSERVATIONS ON STRAIGHT LINES

# A. CCD1 phi = 135

execute(csl_point_source_to_fov, theta=1., phi=45.0, wait=True) # obsid 431
### IT SEEMS IN THE PREV. COMMAND THE SMA DIDN'T POSITION THE SOURCE ON THE RIGHT THETA
### It was automatically corrected


CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)

distorted = True
verbose = True


# STRAIGHT LINES

thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])

phis = np.ones_like(thetas) * 135.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)



# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = .2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) #obsid:432


# B. CCD4 phi = 45
execute(csl_point_source_to_fov, theta=1., phi=45.0, wait=True) # obsid 433

# Beep & SMA doesn't end up at the right theta
# Change SMA mechanisms speeds to 15000 each (Big RS was already at 15000)
execute(csl_point_source_to_fov, theta=1., phi=45.0, wait=True) # obsid 434

# Commanding the small RS to 0. from the GUI -- didn't work
# Error message: "10060. Closed loop failed. Deviation exceeds threshold"
# Rik clears the error message

execute(csl_point_source_to_fov, theta=6., phi=45.0, wait=True) # obsid 435
# Not much happens (small movement , 0.5 deg instead of 1, same error message)
# same error message on the small rotation stage

# Rik commands it to 0 from Leuven. It moves halfway only (from 3. to 1.5)
# Finally we command it very close to where it is (1.6 vs 1.5959) and it works
# Then 1.5, 1.0 and finally 0.. That works

execute(csl_point_source_to_fov, theta=1., phi=45.0, wait=True) # obsid 436


thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])

phis = np.ones_like(thetas) * 45.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) #obsid:437

# C. CCD3 phi = -45
execute(csl_point_source_to_fov, theta=1., phi=-45.0, wait=True) # obsid 438

thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])

phis = np.ones_like(thetas) * -45.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) #obsid:439


# D. CCD2 phi = -135
execute(csl_point_source_to_fov, theta=1., phi=-135.0, wait=True) # obsid 440

thetas = np.array([1., 1.5, 2., 2.5, 3.1, 4., 5., 6., 7., 8.3, 10., 12.4, 14., 16.33, 18.])

phis = np.ones_like(thetas) * -135.

angles = np.vstack([thetas,phis]).T
ccdrows, ccdcols, ccdcodes, ccdsides = angles_to_ccd_coordinates(angles, distorted=distorted, verbose=verbose)

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width) #obsid:441


execute(csl_point_source_to_fov, theta=0., phi=0.0, wait=True) # obsid 442

# END OF THE DAY - SWOFF
execute(aeu.n_cam_sync_disable)
execute(aeu.n_cam_swoff)
execute(ogse.ogse_swoff)

# Stop DPU CS
# Stop FITS generator
