#! /usr/bin/env python3

import logging
import sys

from egse.collimator.fcul.ogse import OGSEProxy
from egse.collimator.fcul.ogse import is_ogse_cs_active
from egse.logger import set_all_logger_levels
from egse.system import Timer

from camtest import camtest_logger

set_all_logger_levels(level=logging.INFO)


def main():

    from rich import print

    camtest_logger.info("Running check-ogse...")

    with Timer():
        is_ogse_cs_active(timeout=1.0)

    if response := is_ogse_cs_active(timeout=1.0):
        with OGSEProxy() as ogse:
            lamp = "[green]ON[/green]" if "ON" in ogse.get_lamp() else "[red]OFF[/red]"
            att_level = ogse.att_get_level()
            # att_moving = ogse.xxx  # add flag if wheel is moving or not
        print(f"OGSE status [green]active[/green], lamp is {lamp}, attenuation is {att_level}")
    else:
        print("OGSE status [red]not active[/red]")


if __name__ == "__main__":
    sys.exit(main())
