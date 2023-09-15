import logging
from pathlib import Path

import invoke
import rich
import sys

from egse.system import chdir
from camtest import camtest_logger

THIS_FILE_LOCATION = Path(__file__).parent
ROOT_PROJECT_FOLDER = THIS_FILE_LOCATION / "../.."

# Make sure the logging messages are also send to the log_cs

CAMTEST_LOGGER = camtest_logger
MODULE_LOGGER = logging.getLogger("camtest.scripts")


def main():
    """
    Update the test scripts on the operational machine.

    The following commands will be executed:

        * git fetch updates

        * git rebase updates/develop

        * python -m pip install -e .
    """

    failed = 0

    with chdir(ROOT_PROJECT_FOLDER):
        rich.print("Updating plato-test-scripts...")

        rich.print("Fetching plato-test-scripts: ........... ", end="")
        try:
            if not (response := invoke.run("git fetch updates", hide=True)):
                raise invoke.exceptions.UnexpectedExit()
            else:
                rich.print("[green]succeeded[/green]")
        except invoke.exceptions.UnexpectedExit as exc:
            MODULE_LOGGER.debug("Couldn't fetch the plato-test-scripts repository:")
            MODULE_LOGGER.debug(f"{response.stderr=}")
            MODULE_LOGGER.debug(f"{exc=!s}")
            rich.print("[red]FAILED[/red]")
            failed += 1

        # The bbid.yaml file is automatically updated by the camtest/core and should be ignored.
        # We might want to undo this at some point when the bbid.yaml content is actually used.

        response = invoke.run("git checkout src/camtest/core/bbid.yaml", hide=True)

        response = invoke.run("git status", hide=True)
        if "Changes not staged for commit" in response.stdout:
            rich.print("[red]You have uncommitted changes, "
                       "unable to install latest test scripts.[/red]")
            rich.print("Please run 'git status' and submit or stash all changes to GitHub.")
            return -1

        rich.print("Installing plato-test-scripts update: .. ", end="")
        try:
            if not (response := invoke.run("git rebase updates/develop", hide=True)):
                raise invoke.exceptions.UnexpectedExit()
            else:
                rich.print("[green]succeeded[/green]")
        except invoke.exceptions.UnexpectedExit as exc:
            rich.print("[red]FAILED[/red]")
            MODULE_LOGGER.info("Couldn't merge/rebase the plato-test-scripts repo:")
            errors = [x for x in str(exc).split('\n') if x.startswith('error')]
            for error_msg in errors:
                MODULE_LOGGER.info(f"{error_msg}")
            MODULE_LOGGER.debug(f"{response.stderr=}")
            MODULE_LOGGER.debug(f"{exc=!s}")
            failed += 1


    # Report the installed release

    # We didn't import camtest.version before, so there is no need to reload in order to have the new version number
    from camtest.version import VERSION, git_version

    if failed == 0:
        import socket
        from egse.system import get_host_ip
        CAMTEST_LOGGER.info(f"Release {VERSION} (git_version={git_version()}) properly installed on {socket.gethostname()} [{get_host_ip()}]")
    else:
        CAMTEST_LOGGER.info(f"Failed to install release {VERSION}.")

    return 0


if __name__ == "__main__":

    sys.exit(main())
