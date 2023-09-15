"""
This module provides helper functions for the demo scripts. Do not use these functions
in your building block definitions.
"""

# This module contains helper functions for making the demo work independently.
# The Setup that is loaded from GlobalState would normally be provided by the configuration
# mananger (a server app) and provide devices that talk to the actual hardware.
# In the demo scripts we do not want this behavior and the Setup is therefore loaded
# from the demo_setup.yaml file and uses the device simulators.

from pathlib import Path

from egse.setup import Setup
from egse.state import GlobalState
from egse.config import find_file, find_root


def load_test_setup():
    yaml_file = find_file(name='demo_setup.yaml', in_dir='demos',
                          root=find_root(Path(__file__).resolve(), tests=('LICENSE',)))

    GlobalState._setup = Setup.from_yaml_file(yaml_file)


if __name__ == "__main__":

    load_test_setup()

    print(f"Loaded Setup from: {GlobalState.setup._filename}")
