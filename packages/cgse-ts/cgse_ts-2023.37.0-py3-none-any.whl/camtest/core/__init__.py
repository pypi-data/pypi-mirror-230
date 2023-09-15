"""
This module provides the core functionality to communicate with the Common-EGSE software
(i.e. `plato-common-egse` package) and to work with observations and building blocks.

## Convenience functions

#### `list_setups()`

Sends a command to the configuration manager to return a list of available/known Setups.
The list will be printed on stdout (terminal, commandline) and sorted by setup id in
reversed order. To filter the list, attributes of the Setup can be passed to match a given value.
```
list_setups(site_id="IAS")
list_setups(site_id="CSL", position=2)
```

#### `load_setup([id])`

Loads a new Setup with the given identifier on the configuration manager and returns this
Setup. When no argument is given, the _current_ Setup is loaded from the configuration manager.

"""
from egse.confman import ConfigurationManagerProxy
from egse.setup import list_setups, get_setup, load_setup, submit_setup
from egse.state import GlobalState
from .exec import building_block
from .exec import execute
from .exec import generate_command_sequence


def get_setup_for_obsid(obsid):
    """
    This is a function to be used for interactive use, it will return the Setup that was used for
    the given obsid.
    """

    try:
        with ConfigurationManagerProxy() as proxy:
            setup = proxy.get_setup_for_obsid(obsid)
        if setup is None:
            print(f"No Setup found for the given obsid: {obsid}")
        return setup
    except ConnectionError as exc:
        print("Could not make a connection with the Configuration Manager, no Setup to show you.")


__all__ = [
    "execute",
    "building_block",
    "generate_command_sequence",
    "list_setups",
    "load_setup",
    "get_setup",
    "submit_setup",
    "get_setup_for_obsid",
    "GlobalState",
]
