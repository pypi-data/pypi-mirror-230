from camtest import start_observation, end_observation
from camtest.commanding import tcs
from egse.setup import load_setup
from rich import print

from egse.tcs import OperatingMode
from egse.tcs import ClosedLoopMode
from egse.tcs.tcs import TCSProxy

setup = load_setup()
print(f"Setup loaded: {setup.get_id()}")

start_observation("Setup TCS EGSE: Configure PI control parameters.")

tcs.stop_task()
tcs.set_operating_mode(mode=OperatingMode.NORMAL)
tcs.set_closed_loop_mode(channel='ch1', mode=ClosedLoopMode.PI_ALG_1)
tcs.set_closed_loop_mode(channel='ch2', mode=ClosedLoopMode.PI_ALG_2)
tcs.set_pi_parameters(channel='ch1', ki=0.0772, kp=40.9651, pmax=8000)
tcs.set_pi_parameters(channel='ch2', ki=0.0001, kp=1.0, pmax=17500)

tcs.set_operating_mode(mode=OperatingMode.EXTENDED)
tcs.set_closed_loop_mode(channel='ch1', mode=ClosedLoopMode.PI_ALG_1)
tcs.set_closed_loop_mode(channel='ch2', mode=ClosedLoopMode.PI_ALG_2)
tcs.set_pi_parameters(channel='ch1', ki=0.0772, kp=40.9651, pmax=17500)
tcs.set_pi_parameters(channel='ch2', ki=0.0001, kp=1.0, pmax=12500)
tcs.start_task()

# The generic set_parameter() function is not implemented in test script,
# we therefore still need the CGSE TCS Proxy.

tcs_proxy = TCSProxy()

tcs_proxy.stop_task()
tcs_proxy.set_operating_mode(OperatingMode.EXTENDED)
tcs_proxy.set_parameter("ch1_tset", 25)
tcs_proxy.set_parameter("ch2_tset", 25)
tcs_proxy.commit()
tcs_proxy.run_task()

# do some other stuff...

tcs_proxy.stop_task()
tcs_proxy.set_operating_mode(OperatingMode.CALIBRATION)
tcs_proxy.commit()
tcs_proxy.run_task()

end_observation()

# Questions:
#
# * What about closed loop or open loop, see error 'not in pi mode'
# * What about averaging: mean (0) or median (1)
