import logging

import time

import numpy as np
from rich import print

from camtest import execute
from camtest import start_observation, end_observation
from camtest.commanding import aeu, dpu, ogse, system_to_idle, system_test_if_idle, system_test_if_initialized, \
    system_to_initialized
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from camtest.commanding.mgse import point_source_to_fov
from camtest.em.em_short_tests import validate_gethk, short_sync_test
from egse.settings import Settings

CCD_SETTINGS = Settings.load("Field-Of-View")

LOGGER = logging.getLogger(__name__)


##############
## csl_swon.py
##############

## AT THIS POINT WE MUST HAVE ALL SYSTEMS-GO


# Position the source in a given position

execute(point_source_to_fov, theta=8.3, phi=-5., wait=True)





# SYSTEM_INITIALIZED

start_observation(description="System_to_initialized")

system_test_if_initialized()

system_to_initialized()

system_test_if_initialized()

end_observation()

## SYSTEM_IDLE

start_observation(description="System_to_idle")

system_test_if_idle()

system_to_idle()

system_test_if_idle()

end_observation()


## INTERNAL SYNC - sanity check

# DUMP mode internal sync
execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())

# INTERNAL SYNC

n_fee_parameters = dict(
    num_cycles=5,
    row_start=4000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side="E",
    exposure_time=0.2)

starttime = time.time()
execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_000
endtime = time.time()

print(f"Duration of the acquisition: {endtime-starttime:.3f} sec")




################################################
## EXERNAL SYNC VALIDATION -- FEE INTERFACE TEST
################################################


# Sync = 25 sec & nominal dump mode
start_observation("Sync enable 25 sec & DUMP mode")  # obsid = CSL_000_

aeu.n_cam_sync_enable(image_cycle_time=25, svm_nom=1, svm_red=0)

dpu.n_cam_to_dump_mode()

print(dpu.n_cam_is_dump_mode())

end_observation()



# PARTIAL READOUT

n_fee_parameters = dict(
    num_cycles=5,
    row_start=4000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side="E")

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000



# half CCD - E

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side="E")

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000


# half CCD - incl parallel overscan

n_fee_parameters = dict(
    num_cycles=5,
    row_start=0,
    row_end=4539,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side="E")

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000



# half CCD - F

execute(point_source_to_fov, theta=16.33, phi=-5., wait=True)

n_fee_parameters["ccd_side"]="F"

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000


# Four half CCDs - E

execute(point_source_to_fov, theta=8.3, phi=-5., wait=True)

n_fee_parameters["ccd_side"]="E"
n_fee_parameters["ccd_order"]=[1,2,3,4]

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000

# Four half CCDs, diff order

n_fee_parameters["ccd_order"]=[2,4,1,3]

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000


# BOTH

n_fee_parameters["ccd_order"]=[1,2,3,4]
n_fee_parameters["ccd_side"]="BOTH"

execute(dpu.n_cam_partial_ccd, **n_fee_parameters)  # OBSID = CSL_000


# FULL STANDARD with BOTH
n_fee_parameters = dict(
    num_cycles=5,
    ccd_side="BOTH")

execute(dpu.n_cam_full_standard, **n_fee_parameters)  # OBSID = CSL_000





######################################
## SHORT SYNC TEST -- ON_LONG_PULSE_DO
######################################

fov_coordinates = [[3.1, 45], [8.3, 24.40]]

execute(short_sync_test,num_subpix=3, num_frames=4, num_bck=2, fov_coordinates=fov_coordinates)
dith_amp = 0.01

execute(short_sync_test,num_subpix=3, num_frames=4, num_bck=2, fov_coordinates=fov_coordinates, dith_amp=dith_amp)




#############################################
## VALIDATE THE CHRONOLOGY ISSUE IN 'CIRCLES'
#############################################

# FIRST MAKE SURE WE SHOULD HIT THE TIMEOUT --> SEND IT TO THE OPPOSITE
execute(point_source_to_fov, theta=8.3, phi=171., wait=True)

# PREPARE THE OBS
boresight_angle = 8.3
n_pos = 8

ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
    circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=True)

reverse_order = False
angles, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
                                                                 [ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],
                                                                 reverse=reverse_order)

print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
c = 0
for angle, crow, ccol, ccode, ccd_side in zip(angles, ccdrows, ccdcols, ccdcodes, ccdsides):
    print(
        f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
    c += 1


# Nb of rows to readout
width = 1500

# Exposure time (cycle_time = exposure_time + readout_time)
exposure_time = 0.2

# Number of cycles: nb of images to acquire at every FoV position.
num_cycles = 5

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)



###################################################
## DELAY IN SMC HK DUE TO A NON-RESPONSIVE SMC CS ?
###################################################

start_observation("cam_aat_050_ambient_recentering - SMC-HK delay investigation")

time.sleep(10.)

cam_aat_050_ambient_recentering(num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)

end_observation()



############################################
## VALIDATE THE SMA CORRECTION
############################################

## FIRST UPDATE csl_point_source_to_fov & reload it

"""
import camtest
reload(camtest)
reload(camtest.commanding.mgse)
reload(camtest.commanding.csl_gse)
from camtest.commanding.mgse import point_source_to_fov
"""

execute(cam_aat_050_ambient_recentering, num_cycles=num_cycles, exposure_time=exposure_time, angles=angles,
        ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccdcodes, ccd_sides=ccdsides, n_rows=width)








############################################
## DYNAMIC RANGE TEST
############################################

# BRING THE SYTEM BACK TO A KNOWN POSITION
execute(point_source_to_fov, theta=8.3, phi=-5, wait=False)


# DUMP MODE INT SYNC
execute(dpu.n_cam_to_dump_mode_int_sync)

print(dpu.n_cam_is_dump_mode())


# ATTENUATION = 0.8
n_fee_parameters = dict(
    num_cycles=5,
    row_start=4000,
    row_end=4509,
    rows_final_dump=4510,
    ccd_order=[3,3,3,3],
    ccd_side="E",
    exposure_time=0.2)

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_000



# ATTENUATION = 1.0
attenuation   = 1.0
exposure_time = 0.1

start_observation(f"OGSE attenuation to {attenuation}")  # obsid =

ogse.set_fwc_fraction(fwc_fraction=attenuation)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())

end_observation()

n_fee_parameters["exposure_time"]=exposure_time

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_000


# ATTENUATION

attenuation = "not-set"
exposure_time = "not-set"

start_observation(f"OGSE attenuation to {attenuation}")  # obsid =

ogse.set_fwc_fraction(fwc_fraction=attenuation)

# print(ogse.att_get_factor())
print(ogse.get_relative_intensity())
# print(ogse.att_is_ready())
print(ogse.attenuator_is_ready())


end_observation()

n_fee_parameters["exposure_time"] = exposure_time

execute(dpu.n_cam_partial_int_sync, **n_fee_parameters)  # OBSID = CSL_000





############################################
## GET_HOUSEKEEPING
############################################

#execute(point_source_to_fov, theta=8.3, phi=-5, wait=True)

phis = np.linspace(-171,171,10)

execute(validate_gethk, theta=8.3, phis=phis, tolerance=0.05, time_granularity=2.)
