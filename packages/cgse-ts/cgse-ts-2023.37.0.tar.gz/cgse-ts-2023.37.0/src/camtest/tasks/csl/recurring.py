from gui_executor.exec import exec_recurring_task
from gui_executor.exec import StatusType

from egse.state import GlobalState


@exec_recurring_task(status_type=StatusType.PERMANENT)
def show_setup_and_obs_id():
    from egse.confman import ConfigurationManagerProxy
    from egse.obsid import ObservationIdentifier

    obsid: ObservationIdentifier
    with ConfigurationManagerProxy() as cm_proxy:
        if obsid := cm_proxy.get_obsid().return_code:
            test_id = f"OBSID = {obsid.test_id}, "
        else:
            test_id = ''

    return f"{test_id}Setup ID = {int(GlobalState.setup.get_id())}"
