from rich import print

from camtest import load_setup, execute
from camtest.commanding import dpu
from camtest.commanding import system_test_if_idle, system_to_idle, system_to_initialized, system_test_if_initialized
from camtest.commanding.cam_aat_050_ambient_recentering import cam_aat_050_ambient_recentering
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth
from camtest.commanding.mgse import point_source_to_fov
from camtest.commanding.ogse import ogse_swon, source_is_on
from egse.stages.huber.smc9300 import HuberSMC9300Proxy

setup = load_setup()
print(setup)

huber = HuberSMC9300Proxy()

print(huber.info())

# Sets the current position for the axis 1 (BIG) to 0.00

huber.zero(1)
huber.get_current_position(1)
huber.get_current_encoder_position(1)
huber.get_current_encoder_counter_value(1)

# huber.set_slew_speed(15000)  # this is done via the GUI

huber.goto(1, -91, False)  # 11:45
huber.goto(1, -180, False)  # 11:47 - command is refused as expected
huber.goto(1, -177, False)  # 11:48
huber.goto(1, -172, False)  # 11:50
huber.goto(1, 177, False)  # 11:50
huber.goto(1, 176, False)  # 11:56
huber.goto(1, 0, False)  # 11:57

execute(point_source_to_fov, theta=12, phi=0, wait=True)  # 12:25

# GUIs are not responding
# Connection to the smc9300_cs is lost until the command returns

execute(point_source_to_fov, theta=18, phi=45, wait=True)

execute(point_source_to_fov, theta=15, phi=43, wait=False)

execute(point_source_to_fov, theta=0, phi=0, wait=True)

execute(point_source_to_fov, theta=5, phi=10, wait=True)

execute(point_source_to_fov, theta=0, phi=0, wait=True)  # 12:44

execute(point_source_to_fov, theta=6, phi=-160, wait=True)

# Full system tests including FEE Simulator and DPU CS

execute(system_to_initialized)
system_test_if_initialized()
execute(system_to_idle)
system_test_if_idle()

execute(dpu.n_cam_to_dump_mode_int_sync)

# imported the cam_aat_050_ambient_recentering

boresight_angle = 6.85
n_pos = 8

ccdrowsorig, ccdcolsorig, ccd_codesorig, ccd_sidesorig, anglesorig = circle_fov_geometry(n=n_pos, radius=boresight_angle, offset=0.5, cam='n', distorted=True, verbose=False)

reverse_order = False
angles, [ccdrows, ccdcols, ccd_codes, ccd_sides] = sort_on_azimuth(anglesorig, [ccdrowsorig, ccdcolsorig, ccd_codesorig, ccd_sidesorig], reverse=reverse_order)

# Switch on the OGSE to measure the heat dissipation

source_is_on()

execute(ogse_swon)

# before activating the execute this building block, we need to start the feesim and the dpu_cs on the server

execute(cam_aat_050_ambient_recentering,
    num_cycles=4, exposure_time=4, angles=angles, ccd_rows=ccdrows, ccd_cols=ccdcols, ccd_codes=ccd_codes, ccd_sides=ccd_sides, n_rows=300)


# Test OGSE

from egse.collimator.fcul.ogse import OGSEProxy

ogse = OGSEProxy()

ogse.get_lamp()

ogse.ldls_power('off')
ogse.att_set_level_factor(0)
ogse.ldls_operate('off')
