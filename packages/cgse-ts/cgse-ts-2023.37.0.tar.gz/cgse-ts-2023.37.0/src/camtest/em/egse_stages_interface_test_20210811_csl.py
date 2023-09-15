from rich import print

from camtest import load_setup, execute
from camtest.commanding.mgse import point_source_to_fov
from camtest.commanding.ogse import ogse_swoff, ogse_swon
from egse.collimator.fcul.ogse import OGSEProxy
from egse.settings import Settings
from egse.stages.huber.smc9300 import HuberSMC9300Proxy

HUBER_SETTINGS = Settings.load("Huber Controller")

setup = load_setup()
print(setup)

huber = HuberSMC9300Proxy()
print(huber.info())

# This command does not go to the zero position but sets the current position as the zero position!
#huber.zero(HUBER_SETTINGS.SMALL_ROTATION_STAGE)

execute(point_source_to_fov, theta=0.0, phi=0.0, wait=True)
execute(point_source_to_fov, theta=12.4, phi=0.0, wait=True)
huber.goto(axis=HUBER_SETTINGS.SMALL_ROTATION_STAGE, position=-10., wait=True)
huber.goto(axis=HUBER_SETTINGS.SMALL_ROTATION_STAGE, position=-0.6335, wait=True)
huber.goto(axis=HUBER_SETTINGS.SMALL_ROTATION_STAGE, position=-10.6335, wait=True)

execute(point_source_to_fov, theta=12.4, phi=0.0, wait=True)    # 6.2453 degrees, -114.9890 mm

execute(point_source_to_fov, theta=0.0, phi=0.0, wait=True)

execute(point_source_to_fov, theta=16.33, phi=0.0, wait=True)

execute(point_source_to_fov, theta=8.3, phi=0.0, wait=True)

# OGSE testing

execute(ogse_swon)

ogse = OGSEProxy()
execute(ogse.att_set_level_factor, factor=0.5)

execute(ogse_swoff)
