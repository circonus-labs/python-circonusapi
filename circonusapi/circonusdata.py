"""
Circonus Data Fetching API

This module provides simplified methods for data fetching operations.
To gain access to the full functionality use the circonusapi module.
"""

import math
from datetime import datetime

# At the time of this writing circllhist is not available on pip.
# You can get it from: github.com/circonus-labs/libcircllhist/
from circllhist import Circllhist

from . import circonusapi

################################################################################
## Helper Functions

def _caql_infer_type(res):
    if len(res[0]) >= 3 and isinstance(res[0][2], dict):
        return "histogram"
    else:
        return "numeric"

def _fix_time(start, period):
    if isinstance(start, datetime):
        return _fix_time(start.timestamp(), period)
    if not start % period == 0:
        raise Exception(
            "start parameter {} is not divisible by period {}. Use e.g. {} instead.".format(
                start, period, math.floor(start / period)
            )
        )
    return start

################################################################################
## Classes

class CirconusData(object):
    "Circonus data fetching class"

    def __init__(self, token):
        self._api = circonusapi.CirconusAPI(token)

    def caql(self, query, start, period, count):
        """
        Fetch data using CAQL.
        Returns a map: slot_name => list
        Limitations:
        - slots_names are currently output[i]
        - For histogram output only a single slot is returned
        """
        start = _fix_time(start, period)
        params = {
            "query": query,
            "period": period,
            "start": int(start),
            "end": int(start + count * period),
        }
        res = self._api.api_call("GET", "/caql", params=params)["_data"]
        if _caql_infer_type(res) == "histogram":
            # In this case, we have only a single output metric and res looks like:
            # res = [[1467892920, 60, {'1.2e+02': 1, '2': 1, '1': 1}], ... ]
            return {
                "time": [row[0] for row in res],
                "output[0]": [Circllhist.from_dict(row[2]) for row in res],
            }
        else:
            # In the numeric case res looks like this:
            # res = [[1467892920, [1, 2, 3]], [1467892980, [1, 2, 3]], ... ]
            out = {}
            width = len(res[0][1])
            out["time"] = [row[0] for row in res]
            for i in range(width):
                out["output[{}]".format(i)] = [row[1][i] for row in res]
            return out
