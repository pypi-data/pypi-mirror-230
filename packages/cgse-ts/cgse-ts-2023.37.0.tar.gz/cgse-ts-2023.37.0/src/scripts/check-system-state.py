#! /usr/bin/env python3

"""
Check the overall system state:

* are core services running?
* is a Setup loaded in the configuration manager?
* are all devices defined in the Setup started and ready to accept commands?


"""

from camtest.commanding import aeu
import egse.logger.log_cs as log_cs
from egse.aeu.aeu import is_aeu_cs_active
from egse.collimator.fcul.ogse import OGSEProxy
from egse.collimator.fcul.ogse import is_ogse_cs_active
from egse.confman import is_configuration_manager_active
from egse.procman import is_process_manager_cs_active
from egse.setup import load_setup
from egse.storage import is_storage_manager_active

if __name__ == "__main__":
    from rich import print

    # Check all the core services: Log_cs, cm_cs, sm_cs, and pm_cs

    response = log_cs.send_request("status")

    if response.get("status") == "ACK":
        print("logger status [green]active[/green]")
    else:
        print("logger status [red]not active[/red]")

    if response := is_configuration_manager_active(timeout=1.0):
        setup = load_setup()
        setup_id = int(setup.get_id())
        print("configuration manager status [green]active[/green]", end=", ")
        print(f"Setup {setup_id} loaded")
    else:
        print("configuration manager status [red]not active[/red]")

    if response := is_storage_manager_active(timeout=1.0):
        print("storage manager status [green]active[/green]")
    else:
        print("storage manager status [red]not active[/red]")

    if response := is_process_manager_cs_active(timeout=1.0):
        print("process manager status [green]active[/green]")
    else:
        print("process manager status [red]not active[/red]")

    # Check important common services: AEU, DPU, OGSE

    if response := is_aeu_cs_active("CRIO", timeout=1.0):
        print("AEU cRIO status [green]active[/green]")
    else:
        print("AEU cRIO status [red]not active[/red]")

    for aeu_dev in ["PSU1", "PSU2", "PSU3", "PSU4", "PSU5", "PSU6", "AWG1", "AWG2"]:
        if response := is_aeu_cs_active(aeu_dev, timeout=1.0):
            print(f"AEU {aeu_dev} status [green]active[/green]")
        else:
            print(f"AEU {aeu_dev} status [red]not active[/red]")

    print(f"N-CAM is {'[green]ON[/green]' if aeu.n_cam_is_on() else '[red]OFF[/red]'} "
          f"and {'[green]is[/green]' if aeu.n_cam_is_on() else 'is [red]not[/red]'} syncing.")

    if response := is_ogse_cs_active(timeout=1.0):
        with OGSEProxy() as ogse:
            lamp = "[green]ON[/green]" if "ON" in ogse.get_lamp() else "[red]OFF[/red]"
            att_level = ogse.att_get_level()
        print(f"OGSE status [green]active[/green], lamp is {lamp}, attenuation is {att_level}")
    else:
        print("OGSE status [red]not active[/red]")
