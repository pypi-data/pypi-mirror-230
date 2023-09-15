"""
Generate a daily summary of the SYN-HK and of selected TCS-HK  entries, interpolated every minute.
Writes the output to the multi-day directory on the data storage disk.

Author : P. Royer

Version : 20220218 - 0.1 Draft version, submitted with github issue 1779
                         https://github.com/IvS-KULeuven/plato-common-egse/issues/1779
"""

import datetime
import os

from camtest.analysis.functions.hk_utils import get_hk_date_range
from egse.state import GlobalState


def hk_daily_cronjob():
    """
    SYNOPSIS
        hk_daily_cronjob()

    GOAL
    . Read the SYN-HK HK table the previous operational day
    . Interpolate the HK values on a regular time_step = 60 seconds
    . Include a finetime information to the resulting table (in seconds_since_1958)
    . Output the result in ascii (fixed_format)
    """

    dt = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = dt.strftime("%Y%m%d")

    time_step = 60

    datadir = os.environ["PLATO_DATA_STORAGE_LOCATION"] + "/daily/"
    outputdir = datadir.replace("/daily/", "/multi-day/")

    device = "SYN-HK"
    keys = None
    outputfile = outputdir+f"/hk_interpolated_{device}_{yesterday}_step_{time_step}s.txt"
    get_hk_date_range(start_date=yesterday, end_date=yesterday, time_step=time_step, device=device, keys=keys,
                      datadir=datadir, outputfile=outputfile, decimals=6)

    device = "TCS-HK"
    keys = ["GTCS_TRP1_POUT", "GTCS_TRP22_POUT"]
    outputfile = outputdir+f"/hk_interpolated_{device}_{yesterday}_step_{time_step}s.txt"
    get_hk_date_range(start_date=yesterday, end_date=yesterday, time_step=time_step, device=device, keys=keys,
                      datadir=datadir, outputfile=outputfile, decimals=6)


def get_hk_dir():
    """ Return the path to the daily folder in the storage at the testhouse.

    Returns: Path to the daily folder in the storage at the testhouse.
    """

    try:
        return os.environ["PLATO_DATA_STORAGE_LOCATION"] + "/daily/"
    except KeyError:
        site = GlobalState.setup.site_id

        if site == "SRON":
            return "/data/plato-storage/plato-data/daily"
        else:
            return f"/data/{site}/daily"
