#! /usr/bin/env python3

import logging
import sys

from egse.logger import set_all_logger_levels
from egse.system import Timer
from egse.tempcontrol.keithley.daq6510 import DAQ6510Proxy
from egse.tempcontrol.keithley.daq6510_cs import is_daq6510_cs_active

set_all_logger_levels(level=logging.INFO)


def main():

    from rich import print

    with Timer():
        is_daq6510_cs_active(timeout=10.0)

    if response := is_daq6510_cs_active(timeout=10.0):
        with DAQ6510Proxy() as daq:
            ip_address = daq.get_ip_address()
            commanding_port = daq.get_commanding_port()
        print(f"DAQ6510 status [green]active[/green], listening on {ip_address}:{commanding_port}")
    else:
        print("DAQ6510 status [red]not active[/red]")


if __name__ == "__main__":
    sys.exit(main())
