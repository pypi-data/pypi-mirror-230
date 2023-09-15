from rich import print

from camtest import load_setup, execute
from egse.stages.huber.smc9300 import HuberSMC9300Proxy

setup = load_setup()
print(setup)

huber = HuberSMC9300Proxy()

print(huber.info())

# Sets the current position for the axis 1 (BIG) to 0.00

huber.zero(1)
huber.get_current_position(1)  # 0.00
huber.get_current_encoder_position(1)  # -3.1e-05
huber.get_current_encoder_counter_value(1)  # 358013950

huber.goto(1, 10, False)  # 15:16 wall clock
huber.goto(1, -10, False)  # 15:16
huber.goto(1, -91, False)  # 15:16
huber.goto(1, -45, False)  # 15:17
huber.goto(1, -180, False)  # 15:18
huber.get_current_position(1)  # 181.8506
huber.get_error(1)  # ['1500', 'limit switch error']
huber.clear_error(1)

huber.goto(1, 180, False)  # command had no effect, again limit switch error
huber.clear_error(1)
huber.goto(1, -170, False)
huber.clear_error(1)
huber.goto(1, -170, False)
huber.clear_error(1)
huber.goto(1, 0, False)
huber.get_current_position(1)  # 181.8443

huber.move(1, 10, False)
huber.get_current_position(1)  # 191.8443

huber.goto(1, 0, False)  # takes a negative move to go to zero, hit limit switch
huber.get_current_position(1)  # 181.8487 @ 15:30
huber.clear_error(1)

huber.move(1, -180, False)  # didn't move
huber.move(1, 180, False)  # moves to 1.8

huber.goto(1, 180, False)  # 15:36, goes to 176.7877 -> limit
huber.clear_error(1)


# Next is exercise the SMALL rotation stage

huber.set_slew_speed(2, 15000)
huber.zero(2)

huber.move(2, 5, False)

huber.set_slew_speed(3, 15000)
huber.zero(3)

huber.goto(1, 0, False)  # 16:15
huber.goto(2, 0, False)  # 16:18

setup.gse.stages.calibration.height_collimated_beam = 550



from camtest.commanding.csl_gse import csl_point_source_to_fov

execute(csl_point_source_to_fov, theta=3, phi=0, wait=True)
execute(csl_point_source_to_fov, theta=6, phi=0, wait=True)
execute(csl_point_source_to_fov, theta=9, phi=0, wait=True)
execute(csl_point_source_to_fov, theta=12, phi=0, wait=True)

setup.gse.stages.calibration.height_collimated_beam = 523

execute(csl_point_source_to_fov, theta=15, phi=0, wait=True)
execute(csl_point_source_to_fov, theta=18, phi=0, wait=True)
execute(csl_point_source_to_fov, theta=21, phi=0, wait=True)

huber.get_error(2)

execute(csl_point_source_to_fov, theta=0, phi=30, wait=True)
execute(csl_point_source_to_fov, theta=0, phi=-30, wait=True)

huber.move(3, -100, False)

from camtest.commanding.mgse import point_source_to_fov

execute(point_source_to_fov, theta=0, phi=0, wait=False)
