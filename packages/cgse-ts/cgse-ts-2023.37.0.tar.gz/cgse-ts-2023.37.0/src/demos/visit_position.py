from camtest import building_block
from camtest.commanding import move_rotation_stage


@building_block
def visit_position(position=None):
    print(f"Visiting position {position}")

    move_rotation_stage(angle=position*10)
