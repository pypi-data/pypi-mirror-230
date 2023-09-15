"""
This demo shows how to define a simple building block. Building block shall be defined in the camtest.commanding package

"""

from camtest import building_block, generate_command_sequence, execute
from egse.settings import Settings
from egse.state import GlobalState

STAGES_SETTINGS = Settings.load("Huber Controller")

# >>>>> DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION
from demos.helper import load_test_setup
load_test_setup()
# <<<<< DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION


@building_block
def move_rotation_stage(angle=None):
    stages = GlobalState.setup.gse.stages.device
    stages.goto(axis=STAGES_SETTINGS.BIG_ROTATION_STAGE, position=angle, wait=False)


@building_block
def move_sma_rotation(angle=None):
    stages = GlobalState.setup.gse.stages.device
    stages.goto(axis=STAGES_SETTINGS.SMALL_ROTATION_STAGE, position=angle, wait=False)


generate_command_sequence(move_rotation_stage, angle=20)
execute(move_rotation_stage, angle=20)

# In the following two lines, the argument is taken from the 'move_sma_rotation.yaml'
# file in the input folder.

generate_command_sequence(move_sma_rotation)
execute(move_sma_rotation)
