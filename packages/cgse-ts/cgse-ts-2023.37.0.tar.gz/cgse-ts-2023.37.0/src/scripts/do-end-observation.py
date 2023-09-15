#! /usr/bin/env python3

from egse.confman import ConfigurationManagerProxy
from camtest import end_observation

if __name__ == "__main__":

    # Test if there is an observation running

    with ConfigurationManagerProxy() as cm_proxy:
        obsid = cm_proxy.get_obsid().return_code

        if obsid:
            response = input(f"Really stop the currently running observation ({obsid}) [y/N] ? ")
            if response.lower() in ("y", "yes"):
                print(f"ending observation {obsid}..")
                end_observation()
            else:
                print("aborted.")
        else:
            print("No observation is currently running.")
