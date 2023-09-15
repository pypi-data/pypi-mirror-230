import camtest
from camtest.core.bbid import get_bbid_for_func
from camtest.core.exec import building_block
from egse.config import find_file, find_root
from egse.state import GlobalState

# We do not want the bbid functions to save unit test specific building blocks into
# the system bbid.yaml file. The building block are still read from the camtest/bbid.yaml
# file, but written to the tests/bbid.yaml file

camtest.core.bbid.bbid_yaml_filename = find_file(
    'bbid.yaml', in_dir='tests', root=find_root(__file__, tests=('MKDOCS',)))

# Initially, there is no Setup loaded, use the load_setup() method to load the current Setup
# from the configuration manager.

GlobalState.load_setup()


def test_loading():
    """Load the existing BBIDs and inspect them."""

    from camtest.commanding import hk_only

    bbid = get_bbid_for_func(hk_only)

    assert bbid == "BBID80B3C6F4DF40323B"

    @building_block
    def new_bb_2(value):
        return value

    bbid = get_bbid_for_func(new_bb_2)

    assert bbid
