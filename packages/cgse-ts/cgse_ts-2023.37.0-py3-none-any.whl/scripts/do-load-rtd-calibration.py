from camtest import start_observation, end_observation
from camtest.commanding import tcs
from egse.setup import load_setup
from rich import print

setup = load_setup()
print(setup.gse)

start_observation("Setup TCS EGSE: load RTD calibration.")
tcs.load_rtd_calibration()
end_observation()
