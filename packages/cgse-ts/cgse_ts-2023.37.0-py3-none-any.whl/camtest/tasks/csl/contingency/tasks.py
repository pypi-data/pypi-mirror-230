from gui_executor.utils import copy_func

# Create a group of buttons for status information

group_name = "Status Information"

from camtest.tasks.shared.camera.n_fee import print_register_map
from camtest.tasks.shared.camera.aeu import generate_aeu_report

print_register_map = copy_func(print_register_map, group_name)
generate_aeu_report = copy_func(generate_aeu_report, group_name)

# Create another group of buttons for emergency

group_name = "Emergency STOP"

from camtest.tasks.shared.tcs.taskmanagement import stop_task
from camtest.tasks.csl.gse.hexapod import emergency_stop as hexapod_stop
from camtest.tasks.csl.gse.huber import emergency_stop as huber_stop

stop_task = copy_func(stop_task, group_name, "TCS STOP Task")
hexapod_stop = copy_func(hexapod_stop, group_name, "Hexapod STOP")
huber_stop = copy_func(huber_stop, group_name, "HUBER STOP")
