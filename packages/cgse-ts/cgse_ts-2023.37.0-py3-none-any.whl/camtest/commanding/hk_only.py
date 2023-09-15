import time

from camtest.core.exec import building_block


@building_block
def hk_only(wait_time=None):
    """Retrieve housekeeping telemetry for the given time period.

    This building block will sleep for the given wait time before it returns.

    Args:
        wait_time (int): time period in which the HK TM will be retrieved [seconds]
    """

    time.sleep(wait_time)

