"""
This demo will command the Hexapod into several positions and request the current position on each step.
"""

from camtest import building_block, generate_command_sequence, execute
from camtest.commanding.csl_gse import move_hexapod_relative_user, request_hexapod_user_positions

# >>>>> DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION
from demos.helper import load_test_setup
load_test_setup()
# <<<<< DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION


# We define a simple building block here which performs a relative movement in the
# user reference frame on the CSL Hexapod. The user position before and after the relative
# movement is printed.

@building_block
def operate_hexapod_example():

    user_positions = request_hexapod_user_positions()

    print(f"user_positions: {user_positions}")

    move_hexapod_relative_user(
        translation_x=0, translation_y=0, translation_z=10,
        rotation_x=0, rotation_y=0, rotation_z=0,
        wait=False
    )

    user_positions = request_hexapod_user_positions()

    print(f"user_positions: {user_positions}")


# The generate_command_sequence() can be replaced by execute()

generate_command_sequence(operate_hexapod_example)
