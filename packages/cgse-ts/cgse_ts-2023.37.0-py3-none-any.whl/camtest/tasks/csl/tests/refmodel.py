import os
import textwrap
from pathlib import Path

from gui_executor.exec import Directory
from gui_executor.exec import FileName
from gui_executor.exec import exec_ui

from egse.control import Failure
from egse.setup import get_setup
from egse.setup import load_setup
from egse.setup import submit_setup

UI_MODULE_DISPLAY_NAME = "4 — Setup"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons/"


@exec_ui(display_name="Load Setup")
def load_a_setup(setup_id: int):
    """ Load the setup with the given ID.

    Args:
        - setup_id: Identifier of the setup to load.
    """

    setup = load_setup(setup_id)
    if setup is None:
        print("[red]Setup could not be loaded. Please check the configuration manager.[/]")
    else:
        print(f"[green]Setup {setup.get_id()} loaded.")


@exec_ui(immediate_run=True)
def list_all_setups():
    """ Print an overview of the available setups."""

    from egse.setup import list_setups

    list_setups()


@exec_ui(display_name="New RF Model from Excel file",
         icons=(ICON_PATH / "ref-frame.svg", ICON_PATH / "ref-frame-selected.svg"),
         input_request=("Submit [Y/n] ? ", ))
def reference_frame_model_from_file(
        filename: FileName = "PLATO-CSL-PL-RP-0000_CSL_RFModel_Achel_v01.xlsx",
        location: Directory = os.environ.get("PLATO_CONF_DATA_LOCATION"),
        setup_id: int = None,
        verbose: bool = True
):
    """ Create a new setup with a new CSL reference model, loaded from the given file.

    The test operator is asked whether the modified setup is to be submitted.  Doing so will automatically push the new
    setup to the plato-cgse-conf repository.

    Args:
        - filename: "CSL output Excel file" = name of the laser-tracker-format Excel file from CSL.
                    The file must contain a sheet "Data" which is the only one read.
        - location: Directory where the input file is located.  By default, location is the directory hosting the
                    setups, represented by the environment variable PLATO_CONF_DATA_LOCATION.
        - setup_id: Identifier of the setup to load.  The setup is affected by this function, as the new CSL reference
                    frame model is added/updated.
        - verbose: Whether to print out verbose information.

    Returns:
        - model: CSL reference frame model, built based on the given spreadsheet.
        - setup: Setup with the new CSL reference frame model included.
        - hexhw: PUNA hexapod proxy (or simulator), configured with the new CSL reference frame model.
    """
    from camtest.commanding.functions.csl_functions import csl_model_from_file, prepare_hexapod

    if (setup := get_setup(setup_id)) is None:
        print(textwrap.dedent(f"""\
            Could not get the Setup you requested:

            * Setup ID = {setup_id or "latest Setup"}
            * Check if the Configuration Manager is running
            {"* Check if the given Setup ID is a valid identifier" if setup_id else ""}
        """))
        return None, None

    print(f"Loaded setup {setup.get_id()}.", flush=True)

    print("Creating the model...", flush=True)

    model, setup = csl_model_from_file(filename=str(filename), location=str(location), setup=setup, verbose=verbose)

    print("Configuring the hexapod accordingly...", flush=True)

    hexhw = prepare_hexapod(model=model, setup=None)

    print("Ready to submit the new setup, incl. the new model...", flush=True)
    response = input("Submit [Y/n] ? ")

    if response.lower() == 'y':
        response = submit_setup(setup, "New CSLReferenceFrameModel [csl_model_from_file]")

        if isinstance(response, Failure):
            print(Failure)
            print(textwrap.dedent("""\
                Please note that there was a Failure. The returned Setup contains the updated
                CSL reference model, but has not been properly submitted to the Configuration
                manager and therefore also has not the correct history, not Setup ID.
            """))
        else:
            setup = response  # if no error, the new setup is returned

    return model, setup, hexhw
