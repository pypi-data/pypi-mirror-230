import os
from pathlib import Path

from executor import ExternalCommand

HERE = Path(__file__).parent.resolve()

UI_TAB_ORDER = ['camera', 'tcs', 'tests', 'gse']


def sron_ui():
    logo_path = HERE / "icons/dashboard.svg"

    # On the egse-client, the /data directory is usually mounted read-only.
    # If that is the case, write the command log to the users home folder.

    cmd_log = os.environ.get("PLATO_LOG_FILE_LOCATION")
    if cmd_log is None or not os.access(cmd_log, os.W_OK):
        cmd_log = str(Path("~").expanduser())

    cmd = ExternalCommand(
        f"gui-executor --verbose "
        f"--module-path camtest.tasks.shared.camera "
        f"--module-path camtest.tasks.shared.tcs "
        f"--module-path=camtest.tasks.sron "
        f"--kernel-name plato-test-scripts --single "
        f"--logo {logo_path} --cmd-log {cmd_log} --app-name 'SRON Operator GUI'",
        asynchronous=True
    )
    cmd.start()
