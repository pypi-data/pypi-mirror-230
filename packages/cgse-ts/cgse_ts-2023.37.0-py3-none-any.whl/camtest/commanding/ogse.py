"""
This module defines building blocks and convenience function for the OGSE.  The idea is that only the generic functions
are used in the test scripts.  Under the hood, they call the TH-specific implementation.
"""
import logging

import time

from camtest.core.exec import building_block
from egse.collimator.fcul.ogse import OGSEInterface
from egse.exceptions import Abort
from egse.filterwheel.eksma.fw8smc4 import FilterWheel8SMC4Interface
from egse.filterwheel.eksma.fw8smc5 import Fw8Smc5Interface
from egse.lampcontrol.energetiq.lampEQ99 import LampEQ99Interface
from egse.powermeter.thorlabs.pm100a import ThorlabsPM100Interface
from egse.shutter.thorlabs.ksc101 import ShutterKSC101Interface
from egse.lampcontrol.beaglebone.beaglebone import BeagleboneInterface
from egse.shutter.thorlabs.sc10 import Sc10Interface
from egse.stages.arun.smd3_interface import Smd3Interface
from egse.state import GlobalState
from egse.system import wait_until

LOGGER = logging.getLogger(__name__)

########################
# Switch on/off the OGSE
########################


@building_block
def ogse_swon():
    """ Switch on the OGSE.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_ogse_swon,
        "CSL1": csl_ogse_swon,
        "CSL2": csl_ogse_swon,
        "IAS":  ias_ogse_swon,
        "INTA": inta_ogse_swon,
        "SRON": sron_ogse_swon,
    }

    sitehash[site]()


def csl_ogse_swon():
    """ Switch on the OGSE at CSL.

    This function should never be called from a test script.  Instead, call the generic function ogse_swon().
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    # Power on the power supply for the light source

    ogse.power_on()

    # Set attenuation level factor to 0 i.e. blocking the light source

    ogse.att_set_level_factor(factor=0)

    # Wait to give the system time to power on

    time.sleep(5)

    # Power on the lamp and the laser

    ogse.operate_on()


def inta_ogse_swon():
    """ Switch on the OGSE at INTA.

    This function should never be called from a test script.  Instead, call the generic function ogse_swon().
    """
    setup = GlobalState.setup
    
    lamp: LampEQ99Interface = setup.gse.lamp.device
    filterwheel: FilterWheel8SMC4Interface = setup.gse.filterwheel.device
    powermeter: ThorlabsPM100Interface = setup.gse.powermeter.device
    shutter: Sc10Interface = setup.gse.shutter.device

    # Verify all the devices are correctly connected
    LOGGER.info(f"Is the filterwheel connected? {filterwheel.is_connected()}")
    LOGGER.info(f"Is the shutter connected? {shutter.is_connected()}")
    LOGGER.info(f"Is the powermeter connected? {powermeter.is_connected()}")
    LOGGER.info(f"Is the lamp connected? {lamp.is_connected()}")

    inta_ldls_power_on() # This is the only instrument to be switched on, unless permanent HK from the photodiodes is needed
    # some stabilization time is needed after the ldls lamp is powered
    inta_shutter_close()
    
    powermeter.set_wavelength(setup.gse.powermeter.wavelength)
    wavelength = powermeter.get_wavelength()

    LOGGER.info(f"The powermeter Wavelength is {wavelength}")

    LOGGER.info("The filterwheel will home and this will take some time")
    filterwheel.homing() # puts the wheels into home position
    LOGGER.info(f"The filterwheel is now homed, at the position: {filterwheel.get_position()}")
    # 4. Instruments status check
    LOGGER.info(f"Is the lamp on? {inta_source_is_on()}")
    LOGGER.info(f"Is the shutter closed: {inta_shutter_is_closed()}")

def ias_ogse_swon():
    """ Switch on the OGSE at IAS.

    This function should never be called from a test script.  Instead, call the generic function ogse_swon().
    """
    # Not very sure is this will work together with the already defined BB
    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device
    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device

    #1. Verifies all the devices are correctly connected connected
    LOGGER.info(f"Is the lamp connected? {lamp.is_connected()}")
    LOGGER.info(f"Is the filterwheel connected? {filterwheel.is_connected()}")
    LOGGER.info(f"Is the shutter connected? {shutter.is_connected()}")


    # 2. LAMP switch ON
    ias_ldls_power_on() # This is the only instrument to be switched on, unless permanent HK from the photodiodes is needed
    # some stabilization time is needed after the ldls lamp is powered on

    # 3. Instruments configuration -when applicable-
        # shutter closed and in "single" mode
    ias_shutter_close()
        # filterwheel to TBC position --> Home position proposed, with no filter loaded.
    LOGGER.info("The filterwheel will home and this will take some time")
    filterwheel.homing() # puts the wheels into home position
    LOGGER.info(f"The filterwheel is now homed, at the position: {filterwheel.get_position()}")

    # 4. Instruments status check
    LOGGER.info(f"Is the lamp on? {ias_source_is_on()}")
    LOGGER.info(f"Is the shutter closed: {ias_shutter_is_closed()}")


def sron_ogse_swon():
    """ Switch on the OGSE at SRON.

    This function should never be called from a test script.  Instead, call the generic function ogse_swon().
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device
    powermeter: ThorlabsPM100Interface = GlobalState.setup.gse.powermeter.device
    lamp: BeagleboneInterface = GlobalState.setup.gse.beaglebone_lamp.device

    # Verify all the devices are correctly connected
    LOGGER.info(f"Is the filterwheel connected? {filterwheel.is_connected()}")
    LOGGER.info(f"Is the shutter connected? {shutter.is_connected()}")
    LOGGER.info(f"Is the powermeter connected? {powermeter.is_connected()}")
    LOGGER.info(f"Is the lamp connected? {lamp.is_connected()}")

    sron_shutter_close()
    sron_ldls_power_on()


@building_block
def ogse_swoff():
    """ Switch off the OGSE.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_ogse_swoff,
        "CSL1": csl_ogse_swoff,
        "CSL2": csl_ogse_swoff,
        "IAS":  ias_ogse_swoff,
        "INTA": inta_ogse_swoff,
        "SRON": sron_ogse_swoff,
    }

    sitehash[site]()


def csl_ogse_swoff():

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    # Power off the lamp and the laser

    ogse.operate_off()

    # Set attenuation level factor to 0 i.e. blocking the light source

    ogse.att_set_level_factor(factor=0)

    # Power off the power supply for the light source

    ogse.power_off()


def ias_ogse_swoff():

    #closing the shutter
    ias_shutter_close()

    # power off the lamp
    ias_ldls_power_off()


def inta_ogse_swoff():

    #closing the shutter
    inta_shutter_close()

    # power off the lamp
    inta_ldls_power_off()


def sron_ogse_swoff():

    sron_shutter_close()
    sron_ldls_power_off()


############
# Attenuator
############


def attenuator_is_ready() -> bool:
    """ Check whether the attenuator is ready.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: True of the attenuator is ready; False otherwise.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_attenuator_is_ready,
        "CSL1": csl_attenuator_is_ready,
        "CSL2": csl_attenuator_is_ready,
        "IAS":  ias_attenuator_is_ready,
        "INTA": inta_attenuator_is_ready,
        "SRON": sron_attenuator_is_ready,
    }

    return sitehash[site]()


def csl_attenuator_is_ready() -> bool:
    """ Check whether the attenuator is ready.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function attenuator_is_ready().

    Returns: True of the attenuator is ready; False otherwise.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    return "OK" in ogse.att_status().upper()


def ias_attenuator_is_ready() -> bool:
    """ Check whether the attenuator is ready.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function attenuator_is_ready().

    Returns: True of the attenuator is ready; False otherwise.
    """
    filterwheel = GlobalState.setup.gse.filterwheel.device
    while not filterwheel.has_commands():
        time.sleep(2)
        filterwheel = GlobalState.setup.gse.filterwheel.device

    return filterwheel.get_status()[1] == 0


def inta_attenuator_is_ready() -> bool:
    """ Check whether the attenuator is ready.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function attenuator_is_ready().

    Returns: True of the attenuator is ready; False otherwise.
    """
    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_status()[1] == 0


def sron_attenuator_is_ready() -> bool:
    """ Check whether the attenuator is ready.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function attenuator_is_ready().

    Returns: True of the attenuator is ready; False otherwise.
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_idn() == 'XISM-USB'


def attenuator_is_moving() -> bool:
    """ Check whether the attenuator is moving.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: True if the attenuator is moving; False otherwise.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_attenuator_is_moving,
        "CSL1": csl_attenuator_is_moving,
        "CSL2": csl_attenuator_is_moving,
        "IAS":  ias_attenuator_is_moving,
        "INTA": inta_attenuator_is_moving,
        "SRON": sron_attenuator_is_moving,
    }

    return sitehash[site]()


def csl_attenuator_is_moving() -> bool:
    """ Check whether the attenuator is moving.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function attenuator_is_moving().

    Returns: True if the attenuator is moving; False otherwise.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    return ogse.att_get_level()["att_moving"]


def ias_attenuator_is_moving() -> bool:
    """ Check whether the attenuator is moving.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function attenuator_is_moving().

    Returns: True if the attenuator is moving; False otherwise.
    """

    raise NotImplementedError


def inta_attenuator_is_moving() -> bool:
    """ Check whether the attenuator is moving.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function attenuator_is_moving().

    Returns: True if the attenuator is moving; False otherwise.
    """
    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_status()[1] != 0


def sron_attenuator_is_moving() -> bool:
    """ Check whether the attenuator is moving.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function attenuator_is_moving().

    Returns: True if the attenuator is moving; False otherwise.
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    fw_1_moving, fw_2_moving = filterwheel.is_moving()
    return fw_1_moving or fw_2_moving


@building_block
def set_relative_intensity(relative_intensity: float = None):
    """ Configure the attenuator such that the given relative intensity of the OGSE is reached after passing through.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - relative_intensity: Desired relative intensity of the OGSE after passing through the attenuator w.r.t. before.
                              This is a number between 0 and 1.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_relative_intensity,
        "CSL1": csl_set_relative_intensity,
        "CSL2": csl_set_relative_intensity,
        "IAS":  ias_set_relative_intensity,
        "INTA": inta_set_relative_intensity,
        "SRON": sron_set_relative_intensity,
    }

    sitehash[site](relative_intensity=relative_intensity)
    wait_until(attenuator_is_ready)


def csl_set_relative_intensity(relative_intensity: float = None):
    """
    Configure the attenuator such that the given relative intensity of the OGSE is reached
    after passing through.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for CSL and should never be called from a
    test script.  Instead, call the generic function set_relative_intensity().

    Args:
        relative_intensity: Desired relative intensity of the OGSE after passing through the
            attenuator w.r.t. before. This is a number between 0 and 1.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    ogse.att_set_level_factor(factor=relative_intensity)


def ias_set_relative_intensity(relative_intensity: float = None):
    """ Configure the attenuator such that the given relative intensity of the OGSE is reached after passing through.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function set_relative_intensity().

    Args:
        - relative_intensity: Desired relative intensity of the OGSE after passing through the attenuator w.r.t. before.
                              This is a number between 0 and 1.
    """
    raise NotImplementedError


def inta_set_relative_intensity(relative_intensity: float = None):
    """ Configure the attenuator such that the given relative intensity of the OGSE is reached after passing through.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function set_relative_intensity().

    Args:
        - relative_intensity: Desired relative intensity of the OGSE after passing through the attenuator w.r.t. before.
                              This is a number between 0 and 1.
    """
    raise NotImplementedError


def sron_set_relative_intensity(relative_intensity=None):
    """ Configure the attenuator such that the given relative intensity of the OGSE is reached after passing through.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function set_relative_intensity().

    Args:
        - relative_intensity: Desired relative intensity of the OGSE after passing through the attenuator w.r.t. before.
                              This is a number between 0 and 1.
    """
    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_relative_intensity(relative_intensity)


def get_relative_intensity() -> float:
    """ Return the relative intensity of the OGSE after passing through the attenuator w.r.t. before.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: Relative intensity of the OGSE after passing through the attenuator w.r.t. before.  This is a number
             between 0 and 1.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_get_relative_intensity,
        "CSL1": csl_get_relative_intensity,
        "CSL2": csl_get_relative_intensity,
        "IAS":  ias_get_relative_intensity,
        "INTA": inta_get_relative_intensity,
        "SRON": sron_get_relative_intensity,
    }

    return sitehash[site]()


def csl_get_relative_intensity() -> float:
    """
    Return the relative intensity of the OGSE after passing through the attenuator w.r.t. before.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for CSL and should never be called from a
    test script.  Instead, call the generic function get_relative_intensity().

    Returns:
        Relative intensity of the OGSE after passing through the attenuator w.r.t. before.
        This is a number between 0 and 1.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    return ogse.att_get_level()["att_factor"]


def ias_get_relative_intensity() -> float:
    """ Return the relative intensity of the OGSE after passing through the attenuator w.r.t. before.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function get_relative_intensity().

    Returns: Relative intensity of the OGSE after passing through the attenuator w.r.t. before.  This is a number
             between 0 and 1.
    """

    raise NotImplementedError


def inta_get_relative_intensity() -> float:
    """ Return the relative intensity of the OGSE after passing through the attenuator w.r.t. before.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function get_relative_intensity().

    Returns: Relative intensity of the OGSE after passing through the attenuator w.r.t. before.  This is a number
             between 0 and 1.
    """

    raise NotImplementedError


def sron_get_relative_intensity() -> float:
    """ Return the relative intensity of the OGSE after passing through the attenuator w.r.t. before.

    Meaning of the relative intensity:

        - opaque attenuator: relative intensity of 0 (all light is blocked)
        - transparent attenuator: relative intensity of 1 (all light passes through)

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function get_relative_intensity().

    Returns: Relative intensity of the OGSE after passing through the attenuator w.r.t. before.  This is a number
             between 0 and 1.
    """
    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_relative_intensity()


def get_relative_intensity_by_index():
    """ Return the relative intensity by index.

    Meaning of the relative intensities:

        - 0.0: opaque
        - 1.0: transparent

    Returns: Dictionary with as keys the OGSE attenuation indices, and as values the relative intensities.
    """

    return GlobalState.setup.gse.ogse.calibration.relative_intensity_by_index


@building_block
def set_attenuator_index(index: int = None):
    """ Set the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing through the attenuator w.r.t.
    before) can be assessed via get_relative_intensity_by_index().

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - index: Attenuator index.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_attenuator_index,
        "CSL1": csl_set_attenuator_index,
        "CSL2": csl_set_attenuator_index,
        "IAS":  ias_set_attenuator_index,
        "INTA": inta_set_attenuator_index,
        "SRON": sron_set_attenuator_index,
    }

    sitehash[site](index=index)
    wait_until(attenuator_is_ready)


def csl_set_attenuator_index(index: int = None):
    """ Set the attenuator index of the OGSE.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().

    Args:
        - index: Attenuator index.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    ogse.att_set_level_index(index=index)


def ias_set_attenuator_index(index: int = None):
    """ Set the attenuator index of the OGSE.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().

    Args:
        - index: Attenuator index.
    """

    raise NotImplementedError


def inta_set_attenuator_index(index: int = None):
    """ Set the attenuator index of the OGSE.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().

    Args:
        - index: Attenuator index.
    """

    raise NotImplementedError


def sron_set_attenuator_index(index: int = None):
    """ Set the attenuator index of the OGSE.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().

    Args:
        - index: Attenuator index.
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_position_index(index)


def get_attenuator_index() -> int:
    """ Return the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing through the attenuator w.r.t.
    before) can be assessed via get_relative_intensity_by_index().

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: Attenuator index.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_get_attenuator_index,
        "CSL1": csl_get_attenuator_index,
        "CSL2": csl_get_attenuator_index,
        "IAS":  ias_get_attenuator_index,
        "INTA": inta_get_attenuator_index,
        "SRON": sron_get_attenuator_index,
    }

    return sitehash[site]()


def csl_get_attenuator_index() -> int:
    """ Return the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing
    through the attenuator w.r.t. before) can be assessed via the get_relative_intensity_by_index().

    This function is the implementation specific for CSL and should never be called from
    a test script.  Instead, call the generic function get_attenuator_index().

    Returns:
        Attenuator index.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    return ogse.status()["att_index"]


def ias_get_attenuator_index() -> int:
    """ Return the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing through the attenuator w.r.t.
    before) can be assessed via get_attenuator_index().

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().


    Returns: Attenuator index.
    """

    raise NotImplementedError


def inta_get_attenuator_index() -> int:
    """ Return the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing through the attenuator w.r.t.
    before) can be assessed via get_attenuator_index().

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().


    Returns: Attenuator index.
    """

    raise NotImplementedError


def sron_get_attenuator_index() -> int:
    """ Return the attenuator index of the OGSE.

    How the attenuator index relates to the relative intensity of the OGSE (after passing through the attenuator w.r.t.
    before) can be assessed via get_attenuator_index().

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function set_attenuator_index().


    Returns: Attenuator index.
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_position_index()


@building_block
def set_fwc_fraction(fwc_fraction=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_fwc_fraction,
        "CSL1": csl_set_fwc_fraction,
        "CSL2": csl_set_fwc_fraction,
        "IAS":  ias_set_fwc_fraction,
        "INTA": inta_set_fwc_fraction,
        "SRON": sron_set_fwc_fraction,
    }

    sitehash[site](fwc_fraction=fwc_fraction)
    wait_until(attenuator_is_ready)


def csl_set_fwc_fraction(fwc_fraction=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function ogse_set_fwc_fraction().

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    """

    # Neutral density attenuation factors

    fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    factor = fwc_fraction * fwc_calibration
    ogse.att_set_level_factor(factor=factor)


def ias_set_fwc_fraction(fwc_fraction=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function ogse_set_fwc_fraction().

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    """

    wheel = GlobalState.setup.gse.filterwheel.device
    setup_relat = GlobalState.setup.gse.ogse.calibration.relative_intensity_by_wheel

    fw_positions = setup_relat.positions
    relat_int = setup_relat.intensity

    fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration
    # = 0.001 # if FWC = 1000 is asked, which is no density (0,0), then 1000*0.001 = 1 = relative intensity of (0,
    # 0) which is maximum

    requested_int = fwc_fraction * fwc_calibration

    if requested_int < min(relat_int):
        requested_int = min(relat_int) + 0.01 * min(relat_int)

    if requested_int > max(relat_int):
        requested_int = max(relat_int) - 0.01 * max(relat_int)

    for i in range(len(relat_int) - 1):
        if relat_int[i] <= requested_int <= relat_int[i + 1]:
            index = i

    wheel.set_position(fw_positions[index][0], fw_positions[index][1])



def inta_set_fwc_fraction(fwc_fraction=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function ogse_set_fwc_fraction().

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    """

    setup = GlobalState.setup
    
    wheel = setup.gse.filterwheel.device
    setup_relat = setup.gse.ogse.calibration.relative_intensity_by_wheel

    relat_int = sorted(list(setup_relat.values()))

    fwc_calibration = setup.gse.ogse.calibration.fwc_calibration

    requested_int = fwc_fraction * fwc_calibration

    if requested_int < min(relat_int):
        requested_int = min(relat_int) + 0.01 * min(relat_int)

    if requested_int > max(relat_int):
        requested_int = max(relat_int) - 0.01 * max(relat_int)

    for i in range(len(relat_int) - 1):
        if relat_int[i] <= requested_int < relat_int[i + 1]:
            index = relat_int[i]
        if requested_int == relat_int[i + 1]:
            index = relat_int[i + 1]

    fw_positions = eval([key for key, value in setup_relat.items() if value == index][0])

    wheel.set_position(fw_positions[0], fw_positions[1])

    message = f"The Wheels selection is Pos 1: {fw_positions[0]} and Pos 2: {fw_positions[1]} and the fwc is: {index}."
    print(f"{message}\n")
    continue_test = ""

    while continue_test.upper() not in ("N", "Y"):
        continue_test = input("Do you want to continue with the test, Please make sure that the CS of the FilterWheel in the PM is green before proceeding, as it will not have reached the position yet. (or abort?) \ny (continue) / n (abort)")

    if continue_test.upper() == "N":
        LOGGER.info(f"{message}\n\nAborting test.")
        raise Abort(message)
    else:
        LOGGER.info(f"{message}\n\nContinuing with test.")

def sron_set_fwc_fraction(fwc_fraction=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function ogse_set_fwc_fraction().

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    """

    fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration
    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_relative_intensity(fwc_fraction * fwc_calibration)

def set_fwc_fraction_bandpass(fwc_fraction=None, bandpass=None):

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_fwc_fraction_bandpass,
        "CSL1": csl_set_fwc_fraction_bandpass,
        "CSL2": csl_set_fwc_fraction_bandpass,
        "IAS":  ias_set_fwc_fraction_bandpass,
        "INTA": inta_set_fwc_fraction_bandpass,
        "SRON": sron_set_fwc_fraction_bandpass,
    }

    sitehash[site](fwc_fraction=fwc_fraction, bandpass=bandpass)
    wait_until(attenuator_is_ready)

def csl_set_fwc_fraction_bandpass(fwc_fraction=None, bandpass=None):

    raise NotImplementedError

def ias_set_fwc_fraction_bandpass(fwc_fraction=None, bandpass=None):
    """ Configure the attenuator such that the given fraction of the full-well capacity is reached using only one
    of the wheels and setting the one bearing the bandpass filters to the requested position.

    The specified fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.  E.g. if you
    want to reach the full-well capacity within 6.25s (i.e. a quarter of the nominal image cycle time), the specified
    fraction must be set to 4.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function ogse_set_fwc_fraction_bandpass().

    Args:
        - fwc_fraction: Fraction of the full-well capacity that should be reached in the nominal image cycle time of
                        25s.
    - bandpass: Index in filter wheel 1 of the bandpass filter that is requested (1: Green, 2: Red, 3: NIR).
    """

    wheel = GlobalState.setup.gse.filterwheel.device
    setup_relat = GlobalState.setup.gse.ogse.calibration.relative_intensity_by_single_wheel

    fw_positions = setup_relat.positions
    relat_int = setup_relat.intensity

    fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration

    requested_int = fwc_fraction * fwc_calibration
    index = 0

    if requested_int < min(relat_int):
        requested_int = min(relat_int) + 0.01 * min(relat_int)

    if requested_int > max(relat_int):
        requested_int = max(relat_int) - 0.01 * max(relat_int)

    for i in range(len(relat_int) - 1):
        if relat_int[i] <= requested_int <= relat_int[i + 1]:
            index = i

    wheel.set_position(bandpass, fw_positions[index][1])

def inta_set_fwc_fraction_bandpass(fwc_fraction=None, bandpass=None):

    raise NotImplementedError

def sron_set_fwc_fraction_bandpass(fwc_fraction=None, bandpass=None):

    raise NotImplementedError


@building_block
def set_fw_position(fw_position=None):
    """ Move the filter wheel to desired couple of positions.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - fw_position: Tuple with two positions from 1 to 8. E.g. (1, 1) or (2, 6) or (8, 8)
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_fw_position,
        "CSL1": csl_set_fw_position,
        "CSL2": csl_set_fw_position,
        "IAS":  ias_set_fw_position,
        "INTA": inta_set_fw_position,
        "SRON": sron_set_fw_position,
    }

    sitehash[site](fw_position=fw_position)
    wait_until(attenuator_is_ready)


def csl_set_fw_position(fw_position=None):
    pass


def ias_set_fw_position(fw_position=None):
    filterwheel = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_position(fw_position[0], fw_position[1])


def inta_set_fw_position(fw_position=None):
    filterwheel = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_position(fw_position[0], fw_position[1])

def sron_set_fw_position(fw_position=None):
    pass


# Why there is no @building_block here ??
def get_fwc_fraction() -> float:
    """ Return the fraction of the full-well capacity that is reached within an image cycle time of 25s.

    The fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: Fraction of the full-well capacity that should be reached in the nominal image cycle time of 25s.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_get_fwc_fraction,
        "CSL1": csl_get_fwc_fraction,
        "CSL2": csl_get_fwc_fraction,
        "IAS":  ias_get_fwc_fraction,
        "INTA": inta_get_fwc_fraction,
        "SRON": sron_get_fwc_fraction,
    }

    return sitehash[site]()


def csl_get_fwc_fraction() -> float:
    """
    Return the fraction of the full-well capacity that is reached within an image cycle time of 25s.

    The fraction of the full-well capacity is supposed to be reached for a nominal image cycle
    time of 25s. For shorter/longer image cycles, you must account for the difference in image
    cycle time yourself.

    This function is the implementation specific for CSL and should never be called from a test
    script.  Instead, call the generic function get_fwc_fraction().

    Returns:
        Fraction of the full-well capacity that should be reached in the nominal image cycle
        time of 25s.
    """
    # Neutral density attenuation factors

    fwc_calibration = GlobalState.setup.gse.ogse.calibration.fwc_calibration

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    return ogse.status()["att_factor"] / fwc_calibration


def ias_get_fwc_fraction() -> float:
    """ Return the fraction of the full-well capacity that is reached within an image cycle time of 25s.

    The fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function get_fwc_fraction().

    Returns: Fraction of the full-well capacity that should be reached in the nominal image cycle time of 25s.
    """

    raise NotImplementedError


def inta_get_fwc_fraction() -> float:
    """ Return the fraction of the full-well capacity that is reached within an image cycle time of 25s.

    The fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function get_fwc_fraction().

    Returns: Fraction of the full-well capacity that should be reached in the nominal image cycle time of 25s.
    """

    raise NotImplementedError


def sron_get_fwc_fraction() -> float:
    """ Return the fraction of the full-well capacity that is reached within an image cycle time of 25s.

    The fraction of the full-well capacity is supposed to be reached for a nominal image cycle time of 25s.
    For shorter/longer image cycles, you must account for the difference in image cycle time yourself.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function get_fwc_fraction().

    Returns: Fraction of the full-well capacity that should be reached in the nominal image cycle time of 25s.
    """

    fwc_calibration = GlobalState.setup.gse.ogse.fwc_calibration
    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    return filterwheel.get_relative_intensity() / fwc_calibration


def get_relative_intensity_by_wheel_positions():
    """ Return relative intensity by OGSE filterwheel positions.

    Meaning of the relative intensities:

        - 0.0: opaque
        - 1.0: transparent

    Returns: Dictionary with as keys the OGSE filterwheel positions (as a tuple), and as values the relative intensities.
    """

    return GlobalState.setup.gse.ogse.calibration.relative_intensity_by_wheel


@building_block
def set_attenuator_wheels(wheel_a_pos: int, wheel_b_pos: int):
    """ Set the attenuator wheels to the given positions.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - wheel_a_pos: Requested wheel position A.
        - wheel_b_pos: Requested wheel position B.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_set_att_wheel_positions,
        "CSL1": csl_set_att_wheel_positions,
        "CSL2": csl_set_att_wheel_positions,
        "IAS":  ias_set_att_wheel_positions,
        "INTA": inta_set_att_wheel_positions,
        "SRON": sron_set_att_wheel_positions,
    }

    sitehash[site](wheel_a_pos=wheel_a_pos, wheel_b_pos=wheel_b_pos)
    wait_until(attenuator_is_ready)


def csl_set_att_wheel_positions(wheel_a_pos: int, wheel_b_pos: int):
    """ Set the attenuator wheels to the given positions.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function set_attenuator_wheels().

    Args:
        - wheel_a_pos: Requested wheel position A (between 1 and 8).
        - wheel_b_pos: Requested wheel position B (between 1 and 8).
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    ogse.att_set_level_position(level1=wheel_a_pos, level2=wheel_b_pos)


def ias_set_att_wheel_positions(wheel_a_pos: int, wheel_b_pos: int):
    """ Set the attenuator wheels to the given positions.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function set_attenuator_wheels().

    Args:
        - wheel_a_pos: Requested wheel position A.
        - wheel_b_pos: Requested wheel position B.
    """

    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_set_level_position(wheel_a_pos=wheel_a_pos, wheel_b_pos=wheel_b_pos)


def inta_set_att_wheel_positions(wheel_a_pos: int, wheel_b_pos: int):
    """ Set the attenuator wheels to the given positions.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function set_attenuator_wheels().

    Args:
        - wheel_a_pos: Requested wheel position A.
        - wheel_b_pos: Requested wheel position B.
    """
    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_set_level_position(wheel_a_pos=wheel_a_pos, wheel_b_pos=wheel_b_pos)


def sron_set_att_wheel_positions(wheel_a_pos: int, wheel_b_pos: int):
    """ Set the attenuator wheels to the given positions.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function set_attenuator_wheels().

    Args:
        - wheel_a_pos: Requested wheel position A.
        - wheel_b_pos: Requested wheel position B.
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.set_position_wheels(wheel_a_pos, wheel_b_pos)


@building_block
def intensity_level_up():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_intensity_level_up,
        "CSL1": csl_intensity_level_up,
        "CSL2": csl_intensity_level_up,
        "IAS": ias_intensity_level_up,
        "INTA": inta_intensity_level_up,
        "SRON": sron_intensity_level_up,
    }

    sitehash[site]()


def csl_intensity_level_up():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function intensity_level_up().
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    ogse.att_level_up()


def ias_intensity_level_up():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function intensity_level_up().
    """

    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_level_up()


def inta_intensity_level_up():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function intensity_level_up().
    """
    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_level_up()


def sron_intensity_level_up():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function intensity_level_up().
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.intensity_level_up()


@building_block
def intensity_level_down():
    """ Set the relative intensity for the attenuator the level immediately above the current level.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_intensity_level_down,
        "CSL1": csl_intensity_level_down,
        "CSL2": csl_intensity_level_down,
        "IAS": ias_intensity_level_down,
        "INTA": inta_intensity_level_down,
        "SRON": sron_intensity_level_down,
    }

    sitehash[site]()


def csl_intensity_level_down():
    """ Set the relative intensity for the attenuator the level immediately below the current level.

    This function is the implementation specific for CSL and should never be called from a test script.  Instead, call
    the generic function intensity_level_down().
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device
    ogse.att_level_down()


def ias_intensity_level_down():
    """ Set the relative intensity for the attenuator the level immediately below the current level.

    This function is the implementation specific for IAS and should never be called from a test script.  Instead, call
    the generic function intensity_level_down().
    """

    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_level_down()


def inta_intensity_level_down():
    """ Set the relative intensity for the attenuator the level immediately below the current level.

    This function is the implementation specific for INTA and should never be called from a test script.  Instead, call
    the generic function intensity_level_down().
    """

    filterwheel: FilterWheel8SMC4Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.att_level_down()


def sron_intensity_level_down():
    """ Set the relative intensity for the attenuator the level immediately below the current level.

    This function is the implementation specific for SRON and should never be called from a test script.  Instead, call
    the generic function intensity_level_down().
    """

    filterwheel: Fw8Smc5Interface = GlobalState.setup.gse.filterwheel.device
    filterwheel.intensity_level_down()


##################################
# Laser-Driven Light Source (LDLS)
##################################


def source_is_on() -> bool:
    """ Check whether the OGSE source is on.
    Returns: True if the OGSE source is on; False otherwise.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_source_is_on,
        "CSL1": csl_source_is_on,
        "CSL2": csl_source_is_on,
        "IAS": ias_source_is_on,
        "INTA": inta_source_is_on,
        "SRON": sron_source_is_on,
    }

    return sitehash[site]()


def csl_source_is_on() -> bool:

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    if not ogse.ping():

        return False    # TODO Raise an error instead?

    return "ON" in ogse.get_lamp().upper()


def ias_source_is_on():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    return lamp.get_lamp()


def inta_source_is_on():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    return lamp.get_lamp()


def sron_source_is_on():

    beaglebone: BeagleboneInterface = GlobalState.setup.gse.beaglebone_lamp.device
    return beaglebone.get_lamp_on()



def ias_ldls_power_on():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    lamp.set_lamp(True)



def ias_ldls_power_off():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    lamp.set_lamp(False)


def inta_ldls_power_on():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    lamp.set_lamp(True)


def inta_ldls_power_off():

    lamp: LampEQ99Interface = GlobalState.setup.gse.lamp.device

    lamp.set_lamp(False)




@building_block
def sron_ldls_power_on():
    beaglebone: BeagleboneInterface = GlobalState.setup.gse.beaglebone_lamp.device
    beaglebone.set_lamp(1)


@building_block
def sron_ldls_power_off():
    beaglebone: BeagleboneInterface = GlobalState.setup.gse.beaglebone_lamp.device
    beaglebone.set_lamp(0)


@building_block
def ldls_operate_on():
    """ Operate on the LDLS."""

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    ogse.operate_on()


############
# Powermeter
############


def pm_is_ready():
    """ Check whether the powermeter is ready to use.

    Returns: True if the powermeter is ready to use; False otherwise.
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    pm_status = ogse.pm_status()

    return "OK" in pm_status["pm1"] and "OK" in pm_status["pm2"]


def pm_get_power_and_temperature():
    """ Return the power and temperature for both powermeters.

    Returns: Dictinary with the following entries:
        - "power1": Power measure for powermeter 1 [W].
        - "temp1" Temperature for powermeter 1 [°C].
        - "power2": Power measure for powermeter 2 [W].
        - "temp2" Temperature for powermeter 2 [°C].
    """

    ogse: OGSEInterface = GlobalState.setup.gse.ogse.device

    return ogse.get_power_and_temperature()


def pm_get_power():
    """ Return the power for both powermeters.

    Returns:
        - power1: Power measure for powermeter 1 [W].
        - power2: Power measure for powermeter 2 [W].
    """

    power_and_temp = pm_get_power_and_temperature()

    return power_and_temp["power1"], power_and_temp["power2"]


def pm_get_temperature():
    """ Return the temperature for both powermeters.

    Returns:
        - temp1 Temperature for powermeter 1 [°C].
        - temp2 Temperature for powermeter 2 [°C].
    """

    power_and_temp = pm_get_power_and_temperature()

    return power_and_temp["temp1"], power_and_temp["temp2"]


def ias_pm_get_power():
    powermeter: ThorlabsPM100Interface = GlobalState.setup.gse.powermeter.device

    if powermeter.get_value() > 10:
        powermeter.set_range(auto=True)

    return powermeter.get_value()


def ias_pm_autorange():
    powermeter: ThorlabsPM100Interface = GlobalState.setup.gse.powermeter.device
    powermeter.set_range(auto=True)


def ias_pm_set_zero():
    powermeter: ThorlabsPM100Interface = GlobalState.setup.gse.powermeter.device
    powermeter.set_zero(True)

#########
# Shutter
#########


@building_block
def shutter_close():
    """ Close the shutter, if present.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_shutter_close,
        "CSL1": csl_shutter_close,
        "CSL2": csl_shutter_close,
        "IAS":  ias_shutter_close,
        "INTA": inta_shutter_close,
        "SRON": sron_shutter_close,
    }

    sitehash[site]()


def ias_shutter_close():
    """ Close the shutter at IAS.

    This function should never be called from a test script.  Instead, call the generic function shutter_close().
    """

    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device

    shutter.set_enable(False)


def csl_shutter_close():
    """ Since there is no shutter at CSL, only a warning message will be logged.

    This function should never be called from a test script.  Instead, call the generic function shutter_close().
    """

    LOGGER.warning(
        "You requested to operate the shutter on site CSL. "
        "There is no shutter in CSL. Command is ignored."
    )


def inta_shutter_close():
    """ Close the shutter at INTA.

    This function should never be called from a test script.  Instead, call the generic function shutter_close().
    """

    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device

    if shutter.get_enable():
        shutter.toggle_enable()
        LOGGER.info("The shutter has been closed")
    else:
        LOGGER.info("The shutter is already closed")


def sron_shutter_close():
    """ Close the shutter at SRON.

    This function should never be called from a test script.  Instead, call the generic function shutter_close().
    """

    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device

    if shutter.get_enable():
        shutter.toggle_enable()
        LOGGER.info("The shutter has been closed")
    else:
        LOGGER.info("The shutter is already closed")


@building_block
def shutter_open():
    """ Open the shutter, if present.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_shutter_open,
        "CSL1": csl_shutter_open,
        "CSL2": csl_shutter_open,
        "IAS":  ias_shutter_open,
        "INTA": inta_shutter_open,
        "SRON": sron_shutter_open,
    }

    sitehash[site]()


def csl_shutter_open():
    """ Since there is no shutter at CSL, only a warning message will be logged.

    This function should never be called from a test script.  Instead, call the generic function shutter_open().
    """

    LOGGER.warning(
        "You requested to operate the shutter on site CSL. "
        "There is no shutter in CSL. Command is ignored."
    )


def ias_shutter_open():
    """ Open the shutter at IAS.

    This function should never be called from a test script.  Instead, call the generic function shutter_open().
    """

    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device

    shutter.set_enable(True)
    LOGGER.info("The shutter has been opened")


def inta_shutter_open():
    """ Open the shutter at INTA.

    This function should never be called from a test script.  Instead, call the generic function shutter_open().
    """
    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device
    
    if not shutter.get_enable():
        shutter.toggle_enable()
        LOGGER.info("The shutter has been opened")
    else:
        LOGGER.info("The shutter is already open")


def sron_shutter_open():
    """ Open the shutter at SRON.

    This function should never be called from a test script.  Instead, call the generic function shutter_open().
    """

    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device

    if not shutter.get_enable():
        shutter.toggle_enable()
        LOGGER.info("The shutter has been opened")
    else:
        LOGGER.info("The shutter is already open")


def shutter_is_closed():
    """ Check whether the shutter is closed.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: True if the shutter is closed; False otherwise
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_shutter_is_closed,
        "CSL1": csl_shutter_is_closed,
        "CSL2": csl_shutter_is_closed,
        "IAS":  ias_shutter_is_closed,
        "INTA": inta_shutter_is_closed,
        "SRON": sron_shutter_is_closed,
    }

    return sitehash[site]()


def ias_shutter_is_closed():
    """ Check whether the shutter is closed at IAS.

    This function should never be called from a test script.  Instead, call the generic function shutter_is_closed().

    Returns: True if the shutter is closed; False otherwise
    """

    shutter = GlobalState.setup.gse.shutter.device

    if not shutter.get_enable():

        LOGGER.info("The shutter has been closed")
        return True

    else:

        LOGGER.warning("The shutter is still in an OPEN state")
        return False

    # else:
    #     raise Abort("Shutter is in an undetermined state")


def csl_shutter_is_closed() -> bool:
    """ Check if the shutter is closed at CSL.

    This function should never be called from a test script.  Instead, call the generic function shutter_is_closed().

    Return:
        There is no shutter in CSL, so False is returned.
    """

    # NOTE: This function is called from a generic building_block and therefore we can not Abort
    #       the operation here. But what should then be returned. The building block probably
    #       expects to return a boolean, the correct thing to do would be to return False, but
    #       what would happen then in the function that called this building block?

    return False

    # raise Abort(
    #     "You requested to operate the shutter on site CSL"
    #     "There is no shutter in CSL. Abort"
    # )


def inta_shutter_is_closed() -> bool:
    """ Check if the shutter is closed at INTA.

    This function should never be called from a test script.  Instead, call the generic function shutter_is_closed().

    Returns: True if the shutter is closed; False otherwise
    """

    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device

    if not shutter.get_enable():
        return True
    else:
        return False


def sron_shutter_is_closed() -> bool:
    """ Check if the shutter is closed at SRON.

    This function should never be called from a test script.  Instead, call the generic function shutter_is_closed().

    Returns: True if the shutter is closed; False otherwise
    """

    shutter: Sc10Interface = GlobalState.setup.gse.shutter.device

    if not shutter.get_enable():
        return True
    else:
        return False


@building_block
def shutter_startloop(ccd_number_sync=None, exposure_time=None):
    """ Synchronisation of the shutter with the CCD integration.

    Only to be implemented at IAS (TBD).

    Args:
        - ccd_number_sync: Number of the CCD for which to sync the exposure with opening the shutter (1/2/3/4).
        - exposure_time: Exposure time [s].
    """
    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device

    # force the shutter to stop
    shutter.set_enable(False)

    # TODO To be implemented by IAS

    pass


@building_block
def shutter_stoploop():
    """ Stop the synchronisation of the shutter with the CCD integration.

    Only to be implemented at IAS (TBD).
    """
    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device
    # stops the shutter
    shutter.set_enable(False)
    LOGGER.info("The shutter state is now:", shutter.get_enable())

    # resets the shutter to manual mode
    shutter.set_mode("manual")


@building_block
def shutter_trigger(delay=None, open_time=None):
    """ waits for the given time delay (s). Puts the shutter in single mode, that automatically closes the shutter after
    the specified open time
    Sets the shutter open time duration (s). triggers the shutter opening, that will be automatically closed after the
    open time.

    Only to be implemented at IAS (TBD).
    """

    shutter: ShutterKSC101Interface = GlobalState.setup.gse.shutter.device

    shutter.set_mode("single")      # sets the shutter to single mode
    shutter.set_cycle(open_time, 1, 1)      # open_time, close_time = 1, number of cycles = 1
    time.sleep(delay)   # waits for the time delay
    shutter_open()      # triggers single mode operation

    LOGGER.info(f"shutter is open for {open_time} s")

    while not shutter_is_closed():
        time.sleep(0.1)

    LOGGER.info("Shutter is now closed")


@building_block
def hartmann_select():
    """ Insert the Hartmann mask in the collimator beam.

    Under the hood, this method calls the TH-specific implementation. In test scripts, only this generic function
    should be used, not the TH-specific implementation. It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_hartmann_select,
        "CSL1": csl_hartmann_select,
        "CSL2": csl_hartmann_select,
        "IAS":  ias_hartmann_select,
        "INTA": inta_hartmann_select,
        "SRON": sron_hartmann_select,
    }

    sitehash[site]()


def _hartmann_manual_select(site: str):

    message = f"The selection of the Hartmann mask is a manual operation at {site}.  Verify that it has been " \
              f"inserted, or do it now."
    print(f"{message}\n")
    continue_test = ""

    while continue_test.upper() not in ("N", "Y"):
        print("Was the Hartmann mask inserted (y) or do you wish to abort (n)?")
        continue_test = input()

    if continue_test.upper() == "N":
        LOGGER.info("Aborting (manual) selection of the Hartmann mask.")
        raise Abort("Aborting (manual) selection of the Hartmann mask.")
    else:
        LOGGER.info("Hartmann mask manually selected")


def csl_hartmann_select():
    """ Insert the Hartmann mask in the collimator beam at CSL.

    This function should never be called from a test script.  Instead, call the generic function hartmann_select().
    """

    _hartmann_manual_select("CSL")


def ias_hartmann_select():
    """ Insert the Hartmann mask in the collimator beam at IAS.

    This function should never be called from a test script.  Instead, call the generic function hartmann_select().
    """

    _hartmann_manual_select("IAS")


def inta_hartmann_select():
    """ Insert the Hartmann mask in the collimator beam at INTA.

    This function should never be called from a test script.  Instead, call the generic function hartmann_select().
    """

    _hartmann_manual_select("INTA")


def sron_hartmann_select():
    """ Insert the Hartmann mask in the collimator beam at SRON.

    This function should never be called from a test script.  Instead, call the generic function hartmann_select().
    """

    smd3: Smd3Interface = GlobalState.setup.gse.smd3.device
    smd3.move_mask_fov(True)


@building_block
def hartmann_deselect():
    """ Take the Hartmann mask out of the collimator beam.

    Under the hood, this method calls the TH-specific implementation. In test scripts, only this generic function
    should be used, not the TH-specific implementation. It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_hartmann_deselect,
        "CSL1": csl_hartmann_deselect,
        "CSL2": csl_hartmann_deselect,
        "IAS":  ias_hartmann_deselect,
        "INTA": inta_hartmann_deselect,
        "SRON": sron_hartmann_deselect,
    }

    sitehash[site]()


def _hartmann_manual_deselect(site: str):

    message = f"The deselection of the Hartmann mask is a manual operation at {site}.  Verify that it has been taken " \
              f"out, or do it now."
    print(f"{message}\n")
    continue_test = ""

    while continue_test.upper() not in ("N", "Y"):
        print("Was the Hartmann mask taken out (y) or do you wish to abort (n)?")
        continue_test = input()

    if continue_test.upper() == "N":
        LOGGER.info("Aborting (manual) deselection of the Hartmann mask.")
        raise Abort("Aborting (manual) deselection of the Hartmann mask.")
    else:
        LOGGER.info("Hartmann mask manually deselected")


def csl_hartmann_deselect():
    """ Take the hartmann mask out of the collimator beam at CSL.

    This function should never be called from a test script.  Instead, call the generic function hartmann_deselect().
    """

    _hartmann_manual_deselect("CSL")


def ias_hartmann_deselect():
    """ Take the hartmann mask out of the collimator beam at IAS.

    This function should never be called from a test script.  Instead, call the generic function hartmann_deselect().
    """

    _hartmann_manual_deselect("IAS")


def inta_hartmann_deselect():
    """ Take the hartmann mask out of the collimator beam at INTA.

    This function should never be called from a test script.  Instead, call the generic function hartmann_deselect().
    """

    _hartmann_manual_deselect("INTA")


def sron_hartmann_deselect():
    """ Take the hartmann mask out of the collimator beam at SRON.

    This function should never be called from a test script.  Instead, call the generic function hartmann_deselect().
    """

    smd3: Smd3Interface = GlobalState.setup.gse.smd3.device

    smd3.move_mask_fov(False)


def hartmann_is_selected() -> bool:
    """ Check if the hartmann mechanism is in the collimator beam.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Returns: True if the hartmann is in the field of view; False otherwise
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL":  csl_hartmann_is_selected,
        "CSL1": csl_hartmann_is_selected,
        "CSL2": csl_hartmann_is_selected,
        "IAS":  ias_hartmann_is_selected,
        "INTA": inta_hartmann_is_selected,
        "SRON": sron_hartmann_is_selected,
    }

    return sitehash[site]()


def _hartmann_manual_is_selected():

    message = f"Verify whether the Hartmann mask has been inserted."
    print(f"{message}\n")
    continue_test = ""

    while continue_test.upper() not in ("N", "Y"):
        print("Has the Hartmann mask been inserted ? "
              "\ny (Hartmann mask inserted) / n (Hartmann mask taken out)")
        continue_test = input()

    if continue_test.upper() == "N":
        return False
    else:
        return True


def csl_hartmann_is_selected() -> bool:
    """ Check if the hartmann mechanism is in the collimator beam at CSL.

    This function should never be called from a test script.  Instead, call the generic function hartmann_is_selected().

    Returns: True if the hartmann is in the field of view; False otherwise
    """

    return _hartmann_manual_is_selected()


def ias_hartmann_is_selected() -> bool:
    """ Check if the hartmann mechanism is in the collimator beam at IAS.

    This function should never be called from a test script.  Instead, call the generic function hartmann_is_selected().

    Returns: True if the hartmann is in the field of view; False otherwise
    """

    return _hartmann_manual_is_selected()


def inta_hartmann_is_selected() -> bool:
    """ Check if the hartmann mechanism is in the collimator beam at INTA.

    This function should never be called from a test script.  Instead, call the generic function hartmann_is_selected().

    Returns: True if the hartmann is in the field of view; False otherwise
    """

    return _hartmann_manual_is_selected()


def sron_hartmann_is_selected() -> bool:
    """ Check if the hartmann mechanism is in the collimator beam at SRON.

    This function should never be called from a test script.  Instead, call the generic function hartmann_is_selected().

    Returns: True if the hartmann is in the field of view; False otherwise
    """

    smd3: Smd3Interface = GlobalState.setup.gse.smd3.device
    return smd3.mask_in_fov()
