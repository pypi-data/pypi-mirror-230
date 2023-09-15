""" TEB control.

Usage:

    from camtest.commanding import tgse

    # Set the temperature setpoints

    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_SKY)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_TOU)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_FEE)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_TRP234)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_TRP2)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_TRP3)
    execute(tgse.set_temp_setpoint, trp=tgse.TEB_TRP.TEB_TRP4)

    # Retrieve the temperature setpoints

    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_SKY)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_TOU)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_FEE)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_TRP234)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_TRP2)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_TRP3)
    tgse.get_temperature_setpoint(trp=tgse.TEB_TRP.TEB_TRP4)

    # Start the control loops

    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_SKY)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_TOU)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_FEE)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_TRP234)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_TRP2)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_TRP3)
    execute(tgse.start_control, trp=tgse.TEB_TRP.TEB_TRP4)

    # Stop the control loops()

    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_SKY)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_TOU)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_FEE)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_TRP234)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_TRP2)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_TRP3)
    execute(tgse.stop_control, trp=tgse.TEB_TRP.TEB_TRP4)

"""
import logging
from enum import Enum
from logging import Logger

from camtest import building_block
from egse.state import GlobalState
from egse.tempcontrol.spid.spid import PidInterface

LOGGER: Logger = logging.getLogger(__name__)


class TRP(str, Enum):
    """ Enumeration of the TEB TRP names.

    The TEB TRPs pertain to:

        - the sky shroud;
        - the TOU;
        - the FEE;
        - the MaRi: TRP2, TRP3, and TRP4 (in individually or all at the same time).
    """

    TEB_SKY = "TEB_SKY"
    TEB_TOU = "TEB_TOU"
    TEB_FEE = "TEB_FEE"
    TRP2 = "TRP2"
    TRP3 = "TRP3"
    TRP4 = "TRP4"
    TRP234 = "TRP234"    # --> use when TRP2, TRP3, and TRP4 should be commanded together (same temperature setpoint,...)


@building_block
def set_temp_setpoints(teb_sky: float = None, teb_tou: float = None, teb_fee: float = None,
                       trp2: float = None, trp3: float = None, trp4: float = None):
    """ Set the temperature setpoint for the given TRPs to the given temperatures.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - teb_sky: Temperature to use as TEB_SKY setpoint [°C]
        - teb_tou: Temperature to use as TEB_TOU setpoint [°C]
        - teb_fee: Temperature to use as TEB_FEE setpoint [°C]
        - trp2: Temperature to use as TRP2 setpoint [°C]
        - trp3: Temperature to use as TRP3 setpoint [°C]
        - trp4: Temperature to use as TRP4 setpoint [°C]
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "IAS":  ias_set_temp_setpoints,
        "INTA": inta_set_temp_setpoints,
        "SRON": sron_set_temp_setpoints,
    }

    sitehash[site](teb_sky=teb_sky, teb_tou=teb_tou, teb_fee=teb_fee, trp2=trp2, trp3=trp3, trp4=trp4)


def sron_set_temp_setpoints(teb_sky: float = None, teb_tou: float = None, teb_fee: float = None,
                            trp2: float = None, trp3: float = None, trp4: float = None):
    """ Set the temperature setpoint for the given TRPs to the given temperatures at SRON.

    For all not-None temperatures, the control loop is stopped, the temperature setpoint is configured, and the
    control loop is started again.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoints().

    Args:
        - teb_sky: Temperature to use as TEB_SKY setpoint [°C]
        - teb_tou: Temperature to use as TEB_TOU setpoint [°C]
        - teb_fee: Temperature to use as TEB_FEE setpoint [°C]
        - trp2: Temperature to use as TRP2 setpoint [°C]
        - trp3: Temperature to use as TRP3 setpoint [°C]
        - trp4: Temperature to use as TRP4 setpoint [°C]
    """

    if teb_sky is not None:
        sron_stop_control(trp=TRP.TEB_SKY)
        sron_set_temp_setpoint(trp=TRP.TEB_SKY, temperature=teb_sky)
        sron_start_control(trp=TRP.TEB_SKY)

    if teb_tou is not None:
        sron_stop_control(trp=TRP.TEB_TOU)
        sron_set_temp_setpoint(trp=TRP.TEB_TOU, temperature=teb_tou)
        sron_start_control(trp=TRP.TEB_TOU)

    if teb_fee is not None:
        sron_stop_control(trp=TRP.TEB_FEE)
        sron_set_temp_setpoint(trp=TRP.TEB_FEE, temperature=teb_fee)
        sron_start_control(trp=TRP.TEB_FEE)

    if trp2 is not None:
        sron_stop_control(trp=TRP.TRP2)
        sron_set_temp_setpoint(trp=TRP.TRP2, temperature=trp2)
        sron_start_control(trp=TRP.TRP2)

    if trp3 is not None:
        sron_stop_control(trp=TRP.TRP3)
        sron_set_temp_setpoint(trp=TRP.TRP3, temperature=trp3)
        sron_start_control(trp=TRP.TRP3)

    if trp4 is not None:
        sron_stop_control(trp=TRP.TRP4)
        sron_set_temp_setpoint(trp=TRP.TRP4, temperature=trp4)
        sron_start_control(trp=TRP.TRP4)


def ias_set_temp_setpoints(teb_sky: float = None, teb_tou: float = None, teb_fee: float = None,
                           trp2: float = None, trp3: float = None, trp4: float = None):
    """ Set the temperature setpoint for the given TRPs to the given temperatures at IAS.

    At IAS, this is a manual operation to be performed by the facility.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoints().

    Args:
        - teb_sky: Temperature to use as TEB_SKY setpoint [°C]
        - teb_tou: Temperature to use as TEB_TOU setpoint [°C]
        - teb_fee: Temperature to use as TEB_FEE setpoint [°C]
        - trp2: Temperature to use as TRP2 setpoint [°C]
        - trp3: Temperature to use as TRP3 setpoint [°C]
        - trp4: Temperature to use as TRP4 setpoint [°C]
    """

    if teb_sky is not None:
        ias_set_temp_setpoint(trp=TRP.TEB_SKY, temperature=teb_sky)

    if teb_tou is not None:
        ias_set_temp_setpoint(trp=TRP.TEB_TOU, temperature=teb_tou)

    if teb_fee is not None:
        ias_set_temp_setpoint(trp=TRP.TEB_FEE, temperature=teb_fee)

    if trp2 is not None:
        ias_set_temp_setpoint(trp=TRP.TRP2, temperature=trp2)

    if trp3 is not None:
        ias_set_temp_setpoint(trp=TRP.TRP3, temperature=trp3)

    if trp4 is not None:
        ias_set_temp_setpoint(trp=TRP.TRP4, temperature=trp4)


def inta_set_temp_setpoints(teb_sky: float = None, teb_tou: float = None, teb_fee: float = None,
                            trp2: float = None, trp3: float = None, trp4: float = None):
    """ Set the temperature setpoint for the given TRPs to the given temperatures at INTA.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoints().

    Args:
        - teb_sky: Temperature to use as TEB_SKY setpoint [°C]
        - teb_tou: Temperature to use as TEB_TOU setpoint [°C]
        - teb_fee: Temperature to use as TEB_FEE setpoint [°C]
        - trp2: Temperature to use as TRP2 setpoint [°C]
        - trp3: Temperature to use as TRP3 setpoint [°C]
        - trp4: Temperature to use as TRP4 setpoint [°C]
    """

    if teb_sky is not None:
        inta_set_temp_setpoint(trp=TRP.TEB_SKY, temperature=teb_sky)

    if teb_tou is not None:
        inta_set_temp_setpoint(trp=TRP.TEB_TOU, temperature=teb_tou)

    if teb_fee is not None:
        inta_set_temp_setpoint(trp=TRP.TEB_FEE, temperature=teb_fee)

    if trp2 is not None:
        inta_set_temp_setpoint(trp=TRP.TRP2, temperature=trp2)

    if trp3 is not None:
        inta_set_temp_setpoint(trp=TRP.TRP3, temperature=trp3)

    if trp4 is not None:
        inta_set_temp_setpoint(trp=TRP.TRP4, temperature=trp4)


@building_block
def set_temp_setpoint(trp: TRP = None, temperature: float = None):
    """ Set the temperature setpoint for the given TRP to the given temperature.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    When using "TRP234" (TEB_TRP) as trp, the three TRP's for the Mari (TRP2, TRP3, and TRP4) should be set to the
    same temperature.

    Args:
        - trp: TRP name.
        - temperature: Temperature to use as TRP setpoint [°C].
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "IAS":  ias_set_temp_setpoint,
        "INTA": inta_set_temp_setpoint,
        "SRON": sron_set_temp_setpoint,
    }

    if trp == TRP.TRP234:
        sitehash[site](trp=TRP.TRP2, temperature=temperature)
        sitehash[site](trp=TRP.TRP3, temperature=temperature)
        sitehash[site](trp=TRP.TRP4, temperature=temperature)
    else:
        sitehash[site](trp=trp, temperature=temperature)


def ias_set_temp_setpoint(trp: TRP = None, temperature: float = None):
    """ Set the temperature setpoint for the given TRP to the given temperature at IAS.

    At IAS, this is a manual operation to be performed by the facility.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoint().

    Args:
        - trp: TRP name.
        - temperature: Temperature to use as TRP setpoint [°C].
    """

    print(f"Ask the facility to set the temperature setpoint for {trp.name} to {temperature}°C!")
    print(f"Did the facility set the temperature setpoint for {trp.name} to {temperature}°C? Yes (Y) or no (N)?")

    continue_test = input()

    while continue_test.upper() not in ("N", "Y"):
        continue_test = input()

    if continue_test.upper() == "N":
        message = f"Setting temperature setpoint for {trp.name} aborted"
        LOGGER.warning(message)
    else:
        LOGGER.info(f"Temperature setpoint for {trp.name} set to {temperature}°C")


def inta_set_temp_setpoint(trp: TRP = None, temperature: float = None):
    """ Set the temperature setpoint for the given TRP to the given temperature at INTA.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoint().

    Args:
        - trp: TRP name.
        - temperature: Temperature to use as TRP setpoint [°C].
    """

    print(f"Ask the facility to set the temperature setpoint for {trp.name} to {temperature}°C!")
    print(f"Did the facility set the temperature setpoint for {trp.name} to {temperature}°C? Yes (Y) or no (N)?")

    continue_test = input()

    while continue_test.upper() not in ("N", "Y"):
        continue_test = input()

    if continue_test.upper() == "N":
        message = f"Setting temperature setpoint for {trp.name} aborted"
        LOGGER.warning(message)
    else:
        LOGGER.info(f"Temperature setpoint for {trp.name} set to {temperature}°C")


def sron_set_temp_setpoint(trp: TRP = None, temperature: float = None):
    """ Set the temperature setpoint for the given TRP to the given temperature at SRON.

    This function should never be called from a test script.  Instead, call the generic function set_temp_setpoint().

    Args:
        - trp: TRP name.
        - temperature: Temperature to use as TRP setpoint [°C].
    """

    setup = GlobalState.setup

    heaters = setup.gse.spid.configuration.heaters

    channels = [channel[0] for channel in heaters[trp]]

    tgse: PidInterface = setup.gse.spid.device

    for channel in channels:
        tgse.set_temperature(channel, temperature)


def get_temp_setpoint(trp: TRP = None):
    """ Return the temperature setpoint for the given TRP.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: Temperature setpoint for the given TRP [°C].
    """

    if trp == TRP.TRP234:

        return get_temp_setpoint(trp=TRP.TRP2), get_temp_setpoint(trp=TRP.TRP3), \
               get_temp_setpoint(trp=TRP.TRP4)

    site = GlobalState.setup.site_id

    sitehash = {
        "IAS":  ias_get_temp_setpoint,
        "INTA": inta_get_temp_setpoint,
        "SRON": sron_get_temp_setpoint,
    }

    return sitehash[site](trp=trp)


def ias_get_temp_setpoint(trp: TRP = None):
    """ Return the temperature setpoint for the given TRP at IAS.

    This function should never be called from a test script.  Instead, call the generic function get_temp_setpoint().

    Returns: Temperature setpoint for the given TRP [°C].
    """

    raise NotImplementedError


def inta_get_temp_setpoint(trp: TRP = None):
    """ Return the temperature setpoint for the given TRP at INTA.

    This function should never be called from a test script.  Instead, call the generic function get_temp_setpoint().

    Returns: Temperature setpoint for the given TRP [°C].
    """

    raise NotImplementedError


def sron_get_temp_setpoint(trp: TRP = None):
    """ Return the temperature setpoint for the given TRP at SRON.

    This function should never be called from a test script.  Instead, call the generic function get_temp_setpoint().

    Returns: Temperature setpoint for the given TRP [°C].
    """

    setup = GlobalState.setup

    heaters = setup.gse.spid.configuration.heaters

    channels = [channel[0] for channel in heaters[trp]]

    tgse: PidInterface = setup.gse.spid.device

    for heater in channels:
        return tgse.get_temperature(heater)


@building_block
def start_control(trp: TRP = None):
    """ Start the control loop for the given TRP.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - trp: TRP name.
    """

    if trp == TRP.TRP234:

        start_control(trp=TRP.TRP2)
        start_control(trp=TRP.TRP3)
        start_control(trp=TRP.TRP4)

    site = GlobalState.setup.site_id

    sitehash = {
        "IAS": ias_start_control,
        "INTA": inta_start_control,
        "SRON": sron_start_control,
    }

    sitehash[site](trp=trp)


def ias_start_control(trp: TRP = None):
    """ Start the control loop for the given TRP at IAS.

    This function should never be called from a test script.  Instead, call the generic function start_control().

    Args:
        - trp: TRP name.
    """

    pass


def inta_start_control(trp: TRP = None):
    """ Start the control loop for the given TRP at INTA.

    This function should never be called from a test script.  Instead, call the generic function start_control().

    Args:
        - trp: TRP name.
    """

    raise NotImplementedError


def sron_start_control(trp: TRP = None):
    """ Start the control loop for the given TRP at SRON.

    This function should never be called from a test script.  Instead, call the generic function start_control().

    Args:
        - trp: TRP name.
    """

    setup = GlobalState.setup

    heaters = setup.gse.spid.configuration.heaters

    channels = [channel[0] for channel in heaters[trp]]

    tgse: PidInterface = setup.gse.spid.device
    for heater in channels:
        tgse.enable(heater)


@building_block
def stop_control(trp: TRP = None):
    """ Stop the control loop for the given TRP.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - trp: TRP name.
    """

    if trp == TRP.TRP234:

        stop_control(trp=TRP.TRP2)
        stop_control(trp=TRP.TRP3)
        stop_control(trp=TRP.TRP4)

    site = GlobalState.setup.site_id

    sitehash = {
        "IAS": ias_stop_control,
        "INTA": inta_stop_control,
        "SRON": sron_stop_control,
    }

    sitehash[site](trp=trp)


def ias_stop_control(trp: TRP = None):
    """ Stop the control loop for the given TRP at IAS.

    This function should never be called from a test script.  Instead, call the generic function stop_control().

    Args:
        - trp: TRP name.
    """

    pass


def inta_stop_control(trp: TRP = None):
    """ Stop the control loop for the given TRP at INTA.

    This function should never be called from a test script.  Instead, call the generic function stop_control().

    Args:
        - trp: TRP name.
    """

    pass


def sron_stop_control(trp: TRP = None):
    """ Stop the control loop for the given TRP at SRON.

    This function should never be called from a test script.  Instead, call the generic function stop_control().

    Args:
        - trp: TRP name.
    """

    setup = GlobalState.setup

    heaters = setup.gse.spid.configuration.heaters

    channels = [channel[0] for channel in heaters[trp]]

    tgse: PidInterface = setup.gse.spid.device

    for heater in channels:
        tgse.disable(heater)
