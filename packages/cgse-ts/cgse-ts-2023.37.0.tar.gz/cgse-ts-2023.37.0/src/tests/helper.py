"""
This module provides helper functions for the demo scripts. Do not use these functions
in your building block definitions.
"""

# This module contains helper functions for making the demo work independently. The Setup that is loaded
# from GlobalState would normally be provided by the configuration mananger (a server app) and provide
# devices that talk to the actual hardware. In the demo scripts we do not want this behavior and the
# Setup is therefore loaded from the demo_setup.yaml file and uses the device simulators.

from pathlib import Path

from egse.setup import Setup
from egse.state import GlobalState
from egse.config import find_file, find_root


def load_test_setup():
    yaml_file = find_file(name='test_setup.yaml', in_dir='tests',
                          root=find_root(Path(__file__).resolve(), tests=('LICENSE',)))

    # This function is called in execute(), so we need to neutralize it

    GlobalState._reload_setup = lambda: None

    # Now load the fake setup for the unit tests

    GlobalState._setup = Setup.from_yaml_file(yaml_file)


def set_bbid_yaml_filename():

    # We do not want the bbid functions to save unit test specific building blocks into the
    # system bbid.yaml file. The building block are still read from the camtest/bbid.yaml file,
    # but written to the tests/bbid.yaml file.

    import camtest

    camtest.core.bbid.bbid_yaml_filename = \
        find_file('bbid.yaml', in_dir='tests', root=find_root(__file__, tests=('MKDOCS',)))
