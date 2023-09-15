import enum
from pathlib import Path
from typing import List

import time
from gui_executor.exec import exec_ui
from gui_executor.utypes import Callback

from camtest import building_block
from camtest import end_observation
from camtest import start_observation
from egse.state import GlobalState

UI_MODULE_DISPLAY_NAME = "Gimbal"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons"

def values_move_gimbal() -> List:
    return ['Absolute', 'Relative']

def default_move_gimbal() -> int:
    return 0


@exec_ui(display_name="Homing", use_kernel=True,
         icons=(ICON_PATH / "gimbal-homing.svg", ICON_PATH / "gimbal-homing-selected.svg"))
def home_gimbal():
    """
    This function performs a Homing of the Gimbal and waits until the Homing is finished.
    """
    start_observation("Homing the Gimbal")

    try:
        with GlobalState.setup.gse.gimbal.device as gimbal:
            gimbal.homing()
            rc = gimbal.is_homing_done()
            if(rc):
                print(f"[green]Gimbal has now been homed: {rc}[/]", flush=True)
            else:
                 print(f"[red]Gimbal not in homed: {rc}[/]", flush=True)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Gimbal Server, check in the PM GUI if it's running.[/]")

    end_observation()


@exec_ui(display_name="Move Gimbal", use_kernel=True,
         icons=(ICON_PATH / "gimbal.svg", ICON_PATH / "gimbal-selected.svg"))
def move_gimbal(ChangeMove: Callback(values_move_gimbal, name=List, default=default_move_gimbal),
                Rx: float = 0.0,
                Ry: float = 0.0):
    """
    This function move the Gimbal move to the position absolute or relative.
    """
    start_observation("Move the Gimbal")

    try:
        with GlobalState.setup.gse.gimbal.device as gimbal:
            gimbal.goto_zero_position()
            if(ChangeMove == 'Absolute'):
                rc = gimbal.check_absolute_movement(Rx,Ry)
                if(rc[0] != 0):
                    print("[red]ERROR: Invalid movement command.[/]")
                else:
                    gimbal.move_absolute(Rx,Ry)
                    while not gimbal.is_in_position():
                        time.sleep(1.0)
                        print("[green]Gimbal is now in position.[/]", flush=True)
            else:
                rc = gimbal.check_relative_movement(Rx,Ry)
                if(rc[0] != 0):
                    print("[red]ERROR: Invalid movement command.[/]")
                else:
                    gimbal.move_relative(Rx,Ry)
                    while not gimbal.is_in_position():
                        time.sleep(1.0)
                    print("[green]Gimbal is now in position.[/]", flush=True)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Gimbal Control Server, check in the PM GUI if it's running.[/]")
        
    end_observation()


@exec_ui(display_name="Zero Position", use_kernel=True,
         icons=(ICON_PATH / "gimbal-zero.svg", ICON_PATH / "gimbal-zero-selected.svg"))
def zero_gimbal():
    """
    This function brings the Gimbal to the zero position.
    """
    start_observation("Bring the Gimbal to zero position")

    try:
        with GlobalState.setup.gse.gimbal.device as gimbal:
            gimbal.goto_zero_position()
            while not gimbal.is_in_position():
                time.sleep(1.0)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Gimbal Control Server, check in the PM GUI if it's running.[/]")
    else:
        print("[green]Gimbal is now in zero position.[/]", flush=True)

    end_observation()

@exec_ui(immediate_run=True, display_name="Stop Gimbal",
         icons=(ICON_PATH / "stop.svg", ICON_PATH / "stop.svg")
         )
def stop_gimbal():
    """
    Stops the Gimbal.

    This is a Gimbal emergency switch off in case of an out gassing event.
    """

    start_observation("Stop the Gimbal")

    try:
        with GlobalState.setup.gse.gimbal.device as gimbal:
            rc = gimbal.stop()
    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Gimbal Server, check in the PM GUI if it's running.[/]")
    else:
        print(f"[green]Gimbal has now Stop: {rc}.[/]", flush=True)

    end_observation()





@exec_ui(display_name="Status", immediate_run=True, use_kernel=True)
def print_status_gimbal():
    """This function prints a table with the status of the Gimbal."""
    from rich.console import Console
    from rich.table import Table
    try:
        with GlobalState.setup.gse.gimbal.device as gimbal:
            temperature = gimbal.get_motor_temperatures()
            positionUser = gimbal.get_user_positions()
            positionMachine  = gimbal.get_machine_positions()
            actuatorLength = gimbal.get_actuator_length()
            gimbalOfset = gimbal.get_offsets()
            table = Table(title="Gimbal Status Report")

            table.add_column("Parameter")
            table.add_column("Status", no_wrap=True)

            table.add_row("Motor Temperature Tx", str(temperature[0]))
            table.add_row("Motor Temperature Ty", str(temperature[1]))
            table.add_row("Object (in User) Rx", str(positionUser[0]))
            table.add_row("Object (in User) Ry", str(positionUser[1]))
            table.add_row("Platform (in Machine) Rx", str(positionMachine[0]))
            table.add_row("Platform (in Machine) Ry", str(positionMachine[1]))
            table.add_row("Actuator Length Ry", str(actuatorLength[0]))
            table.add_row("Actuator Length Ry", str(actuatorLength[1]))
            table.add_row("Gimbal Offset Ry", str(gimbalOfset[0]))
            table.add_row("Gimbal Offset Ry", str(gimbalOfset[1]))          
            console = Console(width=80)
            console.print(table)

    except ConnectionError as exc:
        print("[red]ERROR: Could not connect to the Gimbal.[/]")




@building_block
def gimbal_calibration():
    import time
    import sys
    from invoke import Failure

    import numpy as np
    from datetime import datetime

    from egse.config import find_file
    from egse.gimbal import GimbalError
    from egse.gimbal.symetrie.gimbal import GimbalController, GimbalSimulator, GimbalProxy
    from egse.process import SubProcess
    from egse.services import ServiceProxy
    from egse.settings import Settings
    from egse.system import wait_until, AttributeDict
    from egse.control import Failure

    CTRL_SETTINGS = Settings.load("Gimbal Control Server")

    # Gimbal = GimbalController
    Gimbal = GimbalProxy
    #Gimbal = GimbalSimulator

    # Conversion constants
    ARCSEC2DEG = 1. / 3600.

    #
    # POINT DEFINITION
    #
    # Since these positions are special (e.g. corners and centers of the CCDs) it is
    # a good idea to give them symbolic names, so that they are easier to handle
    # in the long run.
    #

    PLATO_CCD_WIDTH  = 18. # PLATO's individual CCD width  (deg)
    PLATO_CCD_HEIGHT = 18. # PLATO's individual CCD height (deg)
    PLATO_CENTER     = 0.  # PLATO's center between CCDs   (deg)

    PLATO_CCD_X0     = PLATO_CCD_WIDTH  / 2 # PLATO's CCD horizontal center (deg)
    PLATO_CCD_Y0     = PLATO_CCD_HEIGHT / 2 # PLATO's CCD vertical center (deg)

    PLATO_UP         = PLATO_CENTER + PLATO_CCD_HEIGHT # deg
    PLATO_DOWN       = PLATO_CENTER - PLATO_CCD_HEIGHT # deg
    PLATO_LEFT       = PLATO_CENTER - PLATO_CCD_WIDTH  # deg
    PLATO_RIGHT      = PLATO_CENTER + PLATO_CCD_WIDTH  # deg

    # Corner points (name, X, Y)
    PLATO_P1 = ("P1", PLATO_CENTER, PLATO_CENTER)
    PLATO_P2 = ("P2", PLATO_CENTER, PLATO_UP)
    PLATO_P3 = ("P3", PLATO_RIGHT,  PLATO_UP)
    PLATO_P4 = ("P4", PLATO_RIGHT,  PLATO_CENTER)
    PLATO_P5 = ("P5", PLATO_RIGHT,  PLATO_DOWN)
    PLATO_P6 = ("P6", PLATO_CENTER, PLATO_DOWN)
    PLATO_P7 = ("P7", PLATO_LEFT,   PLATO_DOWN)
    PLATO_P8 = ("P8", PLATO_LEFT,   PLATO_CENTER)
    PLATO_P9 = ("P9", PLATO_LEFT,   PLATO_UP)

    # CCD centers (name, X, Y)
    PLATO_R1 = ("R1", PLATO_CENTER + PLATO_CCD_X0, PLATO_CENTER + PLATO_CCD_Y0)
    PLATO_R2 = ("R2", PLATO_CENTER + PLATO_CCD_X0, PLATO_CENTER - PLATO_CCD_Y0)
    PLATO_R3 = ("R3", PLATO_CENTER - PLATO_CCD_X0, PLATO_CENTER - PLATO_CCD_Y0)
    PLATO_R4 = ("R4", PLATO_CENTER - PLATO_CCD_X0, PLATO_CENTER + PLATO_CCD_Y0)

    #
    # CCD center with respect to Gimbal's standby position
    #

    GIMBAL_RX_CENTER = 0      # deg
    GIMBAL_RY_CENTER = 0      # deg
    GIMBAL_TIMEOUT   = 600    # Gimbal positioning timeout (s)

    def date_prefix():
        now         = datetime.now()
        return now.strftime("%Y/%m/%d %H:%M:%S - ")

    def print_error(str, flush = True):
        print(f'{date_prefix()}\033[1;31m[ERROR]:\033[0m {str}', end = '\n' if flush else '')
        if not flush:
            sys.stdout.flush()

    def print_info(str, flush = True):
        print(f'{date_prefix()}\033[1;36m [INFO]:\033[0m  {str}', end = '\n' if flush else '')
        if not flush:
            sys.stdout.flush()

    def uniform_around(center, radius, count = 1):
        angle = np.random.uniform(0, 2 * np.pi, count)
        rho   = np.sqrt(np.random.uniform(0, 1, count)) * radius

        points = []
        for i in range(count):
            points.append(
                (center[0], center[1] + rho[i] * np.cos(angle[i]),
                center[2] + rho[i] * np.sin(angle[i])))

        return points

    def open_gimbal():
        if Gimbal == GimbalProxy:
            
            gimbal = GimbalProxy(hostname=CTRL_SETTINGS.HOSTNAME)
        else:
            gimbal = Gimbal()
            
        try:
            gimbal.connect()

            if Gimbal == GimbalProxy:
                gimbal.ping()
                if 'info' not in gimbal.get_commands():
                    print_error('Cannot connect to Gimbal proxy: command list not yet populated')
                    return None

                if 'reference frames' not in gimbal.info():
                    print_info('Gimbal proxy: no reference frames. Not good, not terrible.')
            else:
                gimbal.info()
                
        except GimbalError as err:
            print_error(f'Connection failed: {str(err)}')
            return None
        
        return gimbal



    # Test sequence definition
    PLATO_RAND_RADIUS       = 37 * ARCSEC2DEG # Random radius around CCD centers (deg)
    PLATO_RAND_NUM          = 5               # Number of measurements around this position
    PLATO_SEQ_NUM           = 3               # Number of times the full sequence must be repeated
    PLATO_TEST_LOG_TEMPLATE = 'gimbal_plato_'
    PLATO_THERMAL_LOG_TEMPLATE = 'gimbal_plato_thermal_'
    PLATO_MOVE_WAIT         = 60             # Time to sleep between movements (seconds)
    PLATO_READING_INTERVAL  = 1              # Time to sleep between readings while stopped
    fixed_sequence = []

    fixed_sequence.append(PLATO_P1)
    fixed_sequence.append(PLATO_P2)
    fixed_sequence.append(PLATO_P3)
    fixed_sequence.append(PLATO_P4)
    fixed_sequence.append(PLATO_P5)
    fixed_sequence.append(PLATO_P6)
    fixed_sequence.append(PLATO_P7)
    fixed_sequence.append(PLATO_P8)
    fixed_sequence.append(PLATO_P9)
    fixed_sequence.append(PLATO_P1)

    ######################################### Test start ####################################
    print_info('Opening Gimbal...')
    gimbal = open_gimbal()

    if gimbal is None:
        sys.exit(1)

    print_info('Waiting for Gimbal to be in position...')

    if wait_until(gimbal.is_in_position, interval=1, timeout = GIMBAL_TIMEOUT):
        print_error(f'Not in position. Aborting.')
        sys.exit(1)

    print_info(f'Configuring Gimbal center ({GIMBAL_RX_CENTER:g}, {GIMBAL_RY_CENTER:g})...')
    gimbal.configure_offsets(-GIMBAL_RX_CENTER, -GIMBAL_RY_CENTER)

    print_info(f'Homing...')

    gimbal.homing()

    if wait_until(gimbal.is_homing_done, interval=0.5, timeout = GIMBAL_TIMEOUT):
        print_error(f'Homing not done. Aborting.')
        sys.exit(1)

    # Open log file
    now         = datetime.now()
    date_suffix = now.strftime("%Y_%m_%d_%H%M%S")
    logfile     = PLATO_TEST_LOG_TEMPLATE + date_suffix + ".csv"
    thrmfile    = PLATO_THERMAL_LOG_TEMPLATE + date_suffix + ".csv"

    print_info(f'Opening log file \033[1m{logfile}\033[0m...')

    try:
        f = open(logfile, "w")
    except RuntimeError as e:
        print_error(f'Failed to open log file for writing: {str(e)}')
        sys.exit(1)

    print_info(f'Opening thermal log file \033[1m{thrmfile}\033[0m...')

    try:
        tf = open(thrmfile, "w")
    except RuntimeError as e:
        print_error(f'Failed to open thermal log file for writing: {str(e)}')
        sys.exit(1)


    #
    # save_thrm_reading
    #
    # Store readings of the temperature and current axes positions to a file
    #

    def save_thrm_reading(gimbal, tf, p):
        t_0 = datetime.now().timestamp()
        m_T = gimbal.get_motor_temperatures()
        u_p = gimbal.get_user_positions()
        m_p = gimbal.get_machine_positions()

        tf.write(f'{t_0}, {p[0]}, {p[1]}, {p[2]}, {u_p[0]}, {u_p[1]}, {m_p[0]}, {m_p[1]}, {m_T[0]}, {m_T[1]}\n')
        tf.flush()
        
        return t_0, m_T, u_p, m_p
    #
    # in_position
    #
    # This is a convenience function used by wait_until that, in addition to
    # returning whether a movement is complete, provides user feedback of the
    # current state of the actuator angles.
    #

    def in_position(gimbal, tf, p):
        t_0, m_T, u_p, m_p = save_thrm_reading(gimbal, tf, p)
        
        text = f'({u_p[0]:+9.5f}, {u_p[1]:+9.5f})'
        text += len(text) * '\b'
        print(text, end = '')
        sys.stdout.flush()

        return gimbal.is_in_position()

    #
    # observe_data
    #
    # This is a convenience function to observe temperature and position until
    # certain time has elapsed
    #
    def observe_data(gimbal, tf, p, t_start, t_wait):
        t_0, m_T, u_p, m_p = save_thrm_reading(gimbal, tf, p)
        return t_0 - t_start >= t_wait

    def wait_and_observe(gimbal, tf, p, t_wait):
        t_start = datetime.now().timestamp()
        if wait_until(lambda: observe_data(gimbal, tf, p, t_start, t_wait), interval=PLATO_READING_INTERVAL, timeout = 2 * t_wait):
            print_error(f'Time out while saving data. Aborting.')
            sys.exit(1)

    for n in range(PLATO_SEQ_NUM):
        print_info(f'Starting positioning sequence {n + 1}/{PLATO_SEQ_NUM}')
        
        #
        # Some parts of the sequence are fixed, while others are not. The following
        # lines take fixed_sequence as a template from its fixed part, and completes
        # it with random points around the CCD centers.
        #
        # This ensures that, in each repetition of the test sequence, we visit different
        # random points around each CCD center.
        #
        sequence = fixed_sequence.copy()
        
        sequence += uniform_around(PLATO_R1, PLATO_RAND_RADIUS, PLATO_RAND_NUM)
        sequence += uniform_around(PLATO_R2, PLATO_RAND_RADIUS, PLATO_RAND_NUM)
        sequence += uniform_around(PLATO_R3, PLATO_RAND_RADIUS, PLATO_RAND_NUM)
        sequence += uniform_around(PLATO_R4, PLATO_RAND_RADIUS, PLATO_RAND_NUM)

        for p in sequence:
            print_info(f'  GOTO \033[1m{p[0]}\033[0m -> ({p[1]:+9.5f}, {p[2]:+9.5f}) ... ', flush = False)

            t_start = datetime.now().timestamp()
            
            rc = gimbal.move_absolute(p[1], p[2])
            if rc != 0:
                print('failed.')
                print_error('Move absolute failed. Aborting.')
                sys.exit(1)

            if wait_until(lambda: in_position(gimbal, tf, p), interval=.1, timeout = GIMBAL_TIMEOUT):
                print('time out.')
                print_error(f'Time out while positioning. Aborting.')
                sys.exit(1)

            t_end = datetime.now().timestamp()

            # Wait to ensure certain stabilization in the Y axis
            wait_and_observe(gimbal, tf, p, PLATO_MOVE_WAIT)

            u_p = gimbal.get_user_positions()
            m_p = gimbal.get_machine_positions()
            m_T = gimbal.get_motor_temperatures()
            
            err = np.sqrt((u_p[0] - p[1]) ** 2 + (u_p[1] - p[2]) ** 2)
            
            print(f'({u_p[0]:+9.5f}, {u_p[1]:+9.5f}) | Err = {err:+0.5f} deg | {m_T[0]:+5.2f} ºC, {m_T[1]:+5.2f} ºC')

            #
            # ADD TEST CODE HERE. RELEVANT VARIABLES:
            #
            # n: Sequence iteration index (starting from 0)
            #
            # p[0]: symbolic point name
            # p[1]: nominal X position (deg)
            # p[2]: nominal Y position (deg)
            #
            # u_p[0]: achieved X position (deg)
            # u_p[1]: achieved Y position (deg)
            #
            # m_p[0]: Gimbal X-axis position (deg)
            # m_p[1]: Gimbal Y-axis position (deg)
            #
            # m_T[0]: Temperature of the motor of the X axis actuator (degC)
            # m_T[1]: Temperature of the motor of the Y axis actuator (degC)
            #
            # t_start: Timestamp of the request of the movement
            # t_end:   Timestamp of the completion of the movement
            #
            # --------8<------------------------------------------8<-------
            #

            # Implement me!
            
            #
            # --------8<------------------------------------------8<-------
            # Save results to disk.
            
            f.write(f'{n}, {t_start}, {t_end}, {p[0]}, {p[1]}, {p[2]}, {u_p[0]}, {u_p[1]}, {m_p[0]}, {m_p[1]}, {m_T[0]}, {m_T[1]}\n')
            f.flush()
            
        print_info(f'Test sequence done.')
        print_info('')

    f.close()
    tf.close()
    print_info(f'Test finished (movement log stored in {logfile})')
