"""
Usage:

    >>> from camtest import generate_command_sequence
    >>> from demos.visit_4_positions import visit_4_positions
    >>> generate_command_sequence(visit_4_positions)

"""
from camtest import building_block
from demos.visit_position import visit_position

# >>>>> DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION
from demos.helper import load_test_setup
load_test_setup()
# <<<<< DO NOT COPY THESE LINES IN YOUR CODE - ONLY FOR DEMONSTRATION


@building_block
def visit_4_positions():

    for position in [1, 2, 3, 4]:
        print(f"Move to {position}")
        visit_position(position=position)
