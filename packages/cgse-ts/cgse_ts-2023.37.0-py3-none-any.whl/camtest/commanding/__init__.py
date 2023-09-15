"""
This module contains all functions and building_blocks for performing the PLATO camera tests.

The module has a flat structure to enforce clarity and explicit naming which is preferred for
instrument commanding where 'explicit is better than implicit'!

All building blocks shall be imported here and made available through the __all__ variable.

Use explicit and absolute import statements.

"""
import logging

from camtest.commanding import aeu, dpu, ogse, tcs
from camtest.commanding import dpu, tcs, ogse, aeu
from camtest.commanding.csl_gse import hexapod_puna_homing
from camtest.commanding.dpu import _convert_n_fee_parameters
from camtest.core import building_block
from egse.aeu.aeu import IntSwitch
from egse.device import DeviceInterface
from egse.exceptions import Abort
from egse.proxy import Proxy
from egse.setup import Setup
from egse.state import GlobalState
from egse.system import find_class

LOGGER = logging.getLogger(__name__)


def system_test_if_initialized(ask_user_input=True):
    """ Check whether the EGSE is ready to start the test phase.

    At the start of the test phase, the following conditions must be met:

        - The N-CAM is powered on;
        - The AEU is syncing;
        - The N-FEE is in on mode;
        - The OGSE source is on and the shutter is closed;
        - The TCS (if present) is on and is in remote operation mode;
        - The devices (listed in the loaded setup file) are ready to receive commands.

    For each test house, there may be additional requirements.
    """

    setup: Setup = GlobalState.setup

    system_is_initialized = True
    message = "The system is not initialised, because of the following reason(s):\n"

    # Devices (listed in the setup)
    #   - controllers on -> manual procedure!
    #   - ready to accept commands

    devices = {}
    devices = Setup.find_devices(setup, devices=devices)

    for name, device_info in devices.items():

        device_type = device_info[0]
        device_args = device_info[1]

        try:

            with find_class(device_type)(*device_args) as device:

                if isinstance(device, Proxy):

                    if not (device.ping() and device.has_commands()):

                        message += f"- The {name} proxy should be ready to be commanded for the system to be " \
                                   f"initialised.\n"
                        system_is_initialized = False

                elif isinstance(device, DeviceInterface):

                    if not device.is_connected():

                        message += f"- The {name} device (Control Server / Controller) should be ready to be " \
                                   f"commanded for the system to be initialised.\n"
                        system_is_initialized = False

        except ConnectionError:

            message += f"- The {name} device should be connected for the system to be initialised.\n"
            system_is_initialized = False

    # AEU: on and syncing

    if not aeu.n_cam_is_on():

        message += "-The N-CAM must be powered on for the system to be initialised (follow the camera switch-on " \
                   "procedure to recover from this).\n"
        system_is_initialized = False

    if not aeu.n_cam_is_syncing():

        message += "- The AEU must be sending sync signals for the N-CAM for the system to be initialised.\n"
        system_is_initialized = False

    try:
        # DPU: N-FEE in on mode

        if not dpu.n_cam_is_on_mode():
            system_is_initialized = False
            message += "- The N-FEE should be in on mode for the system to be initialised.\n"

        # DPU: No slicing

        if dpu.get_slicing() != 0:
            system_is_initialized = False
            message += "- The DPU slicing parameter should be zero for the system to be initialised.\n"

    except NotImplementedError:

        # DPU down (already checked)
        pass

    # OGSE: source on + shutter closed (no specific attenuation request)

    if not ogse.source_is_on():

        message += "- The OGSE source must be switched on for the system to be initialised.\n"
        system_is_initialized = False

    if "CSL" not in setup.site_id and not ogse.shutter_is_closed():

        message += "- The shutter must be closed for the system to be initialised.\n"
        system_is_initialized = False

    # TCS: -> check if it's present!
    #   - configured in remote operation mode (i.e. accepting commands)

    if "tcs" in setup.gse:

        if not tcs.is_remote_mode_active():

            message += "- The remote mode of the TCS must be active for the system to be initialised.\n"
            system_is_initialized = False

    # Additional required, specific to the different TH

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_system_test_if_initialized,
        "CSL1": csl_system_test_if_initialized,
        "CSL2": csl_system_test_if_initialized,
        "IAS": ias_system_test_if_initialized,
        "INTA": inta_system_test_if_initialized,
        "SRON": sron_system_test_if_initialized,
    }

    th_is_initialized, th_message = sitehash[site]()

    if not th_is_initialized:

        message += f"{th_message}\n"
        system_is_initialized = False

    if system_is_initialized:
        LOGGER.info("EGSE system is initialized.")
    elif ask_user_input:
        ask_user_reply(message)
    else:
        print(message)


def csl_system_test_if_initialized() -> (bool, str):
    """ Check whether the CSL-specific conditions for the system to be initialised are met.

    At the start of the test phase, the following conditions must be met:

        - The hexapod must be homed.

    Returns:
        - True if the CSL-specific requirements for the system to be initialized are met; False otherwise.
        - Corresponding error message.
    """

    th_is_initialized = True
    th_message = ""

    hexapod = GlobalState.setup.gse.hexapod.device

    if not hexapod.is_homing_done():

        th_message += f"- The homing of the hexapod at {GlobalState.setup.site_id} must be done for the system to be " \
                      f"initialised\n"
        th_is_initialized = False

    return th_is_initialized, th_message


def ias_system_test_if_initialized() -> (bool, str):
    """ Check whether the IAS-specific conditions for the system to be initialised are met.

    Returns:
        - True if the IAS-specific requirements for the system to be initialized are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_initialized = True
    th_message = ""

    return th_is_initialized, th_message


def inta_system_test_if_initialized() -> (bool, str):
    """ Check whether the INTA-specific conditions for the system to be initialised are met.

    Returns:
        - True if the INTA-specific requirements for the system to be initialized are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_initialized = True
    th_message = ""

    return th_is_initialized, th_message


def sron_system_test_if_initialized() -> (bool, str):
    """ Check whether the SRON-specific conditions for the system to be initialised are met.

    Returns:
        - True if the SRON-specific requirements for the system to be initialized are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_initialized = True
    th_message = ""

    return th_is_initialized, th_message


@building_block
def system_to_initialized():
    """ Initialisation of the EGSE system.

    Bring the EGSE system in a state, such that it is ready for the test phase.

    At the start of the test phase, the following conditions must be met:

        - The N-CAM is powered on;
        - The AEU is syncing (image cycle time of 25s, camera sync signal, nominal + redundant TCS sync signals);
        - The N-FEE is in on mode;
        - The OGSE source is on and the shutter is closed;
        - The TCS (if present) is on, has no tasks running, and is in remote operation mode;
        - The devices (listed in the loaded setup file) are ready to receive commands.

    For each test house, there may be additional requirements.
    """

    LOGGER.info("Initialising the EGSE system...")

    setup: Setup = GlobalState.setup

    try:
        # DPU: N-FEE in on mode

        if not dpu.n_cam_is_on_mode():
            dpu.n_cam_to_on_mode()

        # DPU: No slicing

        if dpu.get_slicing() != 0:
            dpu.set_slicing(num_cycles=0)

    except NotImplementedError:
        # DPU down (already checked)
        pass

    # OGSE: source on + shutter closed (no specific attenuation request)

    if setup.site_id != "SRON" and not ogse.source_is_on():
        try:
            ogse.ogse_swon()
        except NotImplementedError:
            # OGSE down (already checked)
            pass

    if "CSL" not in setup.site_id and not ogse.shutter_is_closed():
        try:
            ogse.shutter_close()
        except NotImplementedError:
            # OGSE down (already checked)
            pass

    # TCS: -> check if it's present!
    #   - powered on
    #   - no task running
    #   - configured in remote operation mode (i.e. accepting commands) -> new S/W release?

    if "tcs" in setup.gse:

        if not tcs.is_remote_mode_active():

            tcs.activate_remote_mode()

    # Devices (listed in the setup)
    #   - controllers on -> manual procedure!
    #   - ready to accept commands

    # Additional required, specific to the different TH

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_system_to_initialized,
        "CSL1": csl_system_to_initialized,
        "CSL2": csl_system_to_initialized,
        "IAS": ias_system_to_initialized,
        "INTA": inta_system_to_initialized,
        "SRON": sron_system_to_initialized,
    }

    sitehash[site]()

    # At the end of initialising the EGSE system, check whether it succeeded

    system_test_if_initialized(ask_user_input=False)


def csl_system_to_initialized():
    """ CSL-specific initialisation of the EGSE system.

    At the start of the test phase, the following conditions must be met:

        - The hexapod must be homed.
    """
    hexapod = GlobalState.setup.gse.hexapod.device

    if not hexapod.is_homing_done():

        hexapod_puna_homing(wait=True)


def ias_system_to_initialized():
    """ IAS-specific initialisation of the EGSE system.

    At the start of the test phase, the following conditions must be met:

        -
    """

    raise NotImplementedError


def inta_system_to_initialized():
    """ INTA-specific initialisation of the EGSE system.

    At the start of the test phase, the following conditions must be met:

        -
    """

    raise NotImplementedError


def sron_system_to_initialized():
    """ SRON-specific initialisation of the EGSE system.

    At the start of the test phase, the following conditions must be met:

        -
    """
    raise NotImplementedError


###############
# Between tests
###############

def system_test_if_idle(ask_user_input=True):
    """ Check whether the EGSE is ready to start a test.

    At the start of a test, the following conditions must be met:

        - The N-CAM is powered on;
        - The AEU is syncing;
        - The N-FEE is in dump mode;
        - The OGSE source is on and the shutter is closed;
        - The TCS (if present) is on and is in remote operation mode;
        - The devices (listed in the loaded setup file) are ready to receive commands.

    For each test house, there may be additional requirements.
    """

    setup: Setup = GlobalState.setup

    system_is_idle = True
    message = "The system is not idle, because of the following reason(s):\n"

    # Devices (listed in the setup)
    #   - controllers on -> manual procedure!
    #   - ready to accept commands

    devices = {}
    devices = Setup.find_devices(setup, devices=devices)

    for name, device_info in devices.items():

        device_type = device_info[0]
        device_args = device_info[1]

        try:

            with find_class(device_type)(*device_args) as device:

                if isinstance(device, Proxy):

                    if not (device.ping() and device.has_commands()):

                        system_is_idle = False
                        message += f"- The {name} proxy should be ready to be commanded for the system to be idle.\n"

                elif isinstance(device, DeviceInterface):

                    if not device.is_connected():

                        system_is_idle = False
                        message += f"- The {name} device (Control Server / Controller) should be ready to be " \
                                   f"commanded for the system to be idle.\n"

        except ConnectionError:

            system_is_idle = False
            message += f"- The {name} device should be connected for the system to be idle.\n"

    # AEU: on and syncing

    if not aeu.n_cam_is_on():

        system_is_idle = False
        message += "- The N-CAM must be powered on for the system to be idle (follow the camera switch-on " \
                   "procedure to recover from this).\n"

    if not aeu.n_cam_is_syncing():

        system_is_idle = False
        message += "- The AEU must be sending sync signals for the N-CAM for the system to be idle.\n"

    try:
        # DPU: N-FEE in dump mode

        if not dpu.n_cam_is_dump_mode():

            system_is_idle = False
            message += "- The N-FEE should be in dump mode for the system to be idle.\n"

        # DPU: No slicing

        if dpu.get_slicing() != 0:

            system_is_idle = False
            message += "- The DPU slicing parameter should be zero for the system to be idle.\n"

    except NotImplementedError:

        # DPU down (already checked)
        pass

    # OGSE: source on + shutter closed (no specific attenuation request)

    if not ogse.source_is_on():

        system_is_idle = False
        message += "- The OGSE source must be switched on for the system to be idle.\n"

    if "CSL" not in setup.site_id and not ogse.shutter_is_closed():

        system_is_idle = False
        message += "- The shutter must be closed for the system to be idle.\n"

    # TCS: -> check if it's present!
    #   - configured in remote operation mode (i.e. accepting commands) -> new S/W release?

    if "tcs" in setup.gse:

        if not tcs.is_remote_mode_active():

            system_is_idle = False
            message += "- The remote mode of the TCS must be active for the system to be idle.\n"

    # Additional required, specific to the different TH

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_system_test_if_idle,
        "CSL1": csl_system_test_if_idle,
        "CSL2": csl_system_test_if_idle,
        "IAS": ias_system_test_if_idle,
        "INTA": inta_system_test_if_idle,
        "SRON": sron_system_test_if_idle,
    }

    th_is_idle, th_message = sitehash[site]()

    if not th_is_idle:
        message += f"{th_message}\n"
        system_is_idle = False

    if system_is_idle:
        LOGGER.info("EGSE system is idle.")
    elif ask_user_input:
        ask_user_reply(message)
    else:
        print(message)


def csl_system_test_if_idle() -> (bool, str):
    """ Check whether the CSL-specific conditions for the system to be idle are met.

    Returns:
        - True if the CSL-specific requirements for the system to be idle are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_idle = True
    th_message = ""

    return th_is_idle, th_message


def ias_system_test_if_idle() -> (bool, str):
    """ Check whether the IAS-specific conditions for the system to be idle are met.

    Returns:
        - True if the CSL-specific requirements for the system to be idle are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_idle = True
    th_message = ""

    return th_is_idle, th_message


def inta_system_test_if_idle() -> (bool, str):
    """ Check whether the INTA-specific conditions for the system to be idle are met.

    Returns:
        - True if the CSL-specific requirements for the system to be idle are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_idle = True
    th_message = ""

    return th_is_idle, th_message


def sron_system_test_if_idle() -> (bool, str):
    """ Check whether the SRON-specific conditions for the system to be idle are met.

    Returns:
        - True if the CSL-specific requirements for the system to be idle are met; False otherwise.
        - Corresponding error message.
    """

    # TODO
    th_is_idle = True
    th_message = ""

    return th_is_idle, th_message


@building_block
def system_to_idle():
    """ Bringing the EGSE system in an idle state.

    Bring the EGSE system in a state, such that it is ready for a test.

    At the start of a test, the following conditions must be met:

        - The N-CAM is powered on;
        - The AEU is syncing (image cycle time of 25s, camera sync signal, nominal + redundant TCS sync signals);
        - The N-FEE is in dump mode;
        - The OGSE source is on and the shutter is closed;
        - The TCS (if present) is on, has no tasks running, and is in remote operation mode;
        - The devices (listed in the loaded setup file) are ready to receive commands.

    For each test house, there may be additional requirements.
    """

    LOGGER.info("Bringing the EGSE system in an idle state...")

    setup: Setup = GlobalState.setup

    try:
        #  DPU: N-FEE in dump mode

        if not dpu.n_cam_is_dump_mode():

            if not dpu.n_cam_is_standby_mode():
                dpu.n_cam_to_standby_mode()

            # FIXME: This needs to be tested on the real N-FEE. We might need to execute the
            #        following command on_long_pulse_do: on_long_pulse_do(dpu.n_cam_to_dump_mode)
            dpu.n_cam_to_dump_mode()

        # DPU: No slicing

        if dpu.get_slicing() != 0:
            dpu.set_slicing(num_cycles=0)

    except NotImplementedError:
        # DPU down (already checked)
        pass

    # OGSE: source on + shutter closed (no specific attenuation request)

    if setup.site_id != "SRON" and not ogse.source_is_on():
        try:
            ogse.ogse_swon()
        except NotImplementedError:
            # OGSE down (tested already)
            pass

    if "CSL" not in setup.site_id and not ogse.shutter_is_closed():
        try:
            ogse.shutter_close()
        except NotImplementedError:
            # OGSE down (tested already)
            pass

    # TCS: -> check if it's present!
    #   - configured in remote operation mode (i.e. accepting commands) -> new S/W release?

    if "tcs" in setup.gse:

        if not tcs.is_remote_mode_active():

            tcs.activate_remote_mode()

    # Devices (listed in the setup)
    #   - controllers on -> manual procedure!
    #   - ready to accept commands

    # Additional required, specific to the different TH

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_system_to_idle,
        "CSL1": csl_system_to_idle,
        "CSL2": csl_system_to_idle,
        "IAS": ias_system_to_idle,
        "INTA": inta_system_to_idle,
        "SRON": sron_system_to_idle,
    }

    sitehash[site]()

    # At the end of putting the EGSE system in an idle state, check whether it succeeded

    system_test_if_idle(ask_user_input=False)


def csl_system_to_idle():
    """ Bringing the EGSE in an idle state, specifically for CSL.
    """

    # TODO
    pass


def ias_system_to_idle():
    """ Bringing the EGSE in an idle state, specifically for IAS.
    """

    # TODO
    pass


def inta_system_to_idle():
    """ Bringing the EGSE in an idle state, specifically for INTA.
    """

    # TODO
    pass


def sron_system_to_idle():
    """ Bringing the EGSE in an idle state, specifically for SRON.
    """

    # TODO
    pass


def ask_user_reply(message):
    """ Ask the user (in the Python Console) how to proceed.

    If the user is prompted for input, this is because the system is not idle/initialized.  The user should decide
    whether to proceed with the test or to abort.
    """

    print(f"{message}\n")
    continue_test = ""

    while continue_test.upper() not in ("N", "Y"):
        continue_test = input("Do you want to continue with the test (or abort?) \ny (continue) / n (abort)")

    if continue_test.upper() == "N":
        raise Abort(message)
        LOGGER.info(f"{message}\n\nAborting test.")
    else:
        LOGGER.info(f"{message}\n\nContinuing with test.")
