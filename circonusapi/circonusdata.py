"""
Circonus Data Fetching API

This module provides simplified methods for data fetching operations.
To gain access to the full functionality use the circonusapi module.
"""

import math
from datetime import datetime
import warnings

from . import circonusapi

#
# Optional Imports
#

try:
    from circllhist import Circllhist
except ImportError:
    Circllhsit = None


class CirconusData(object):
    "Circonus data fetching class"

    def __init__(self, token):
        self._api = circonusapi.CirconusAPI(token)

    def caql(self, query, start, period, count):
        """
        Fetch data using CAQL.

        Args:
           query (str): the CAQL query string
           start (int/dateimte): starttime of the query. Either UNIX timestamp in seconds 
                 or datetime object
           period (int): period of data to fetch
           count (int): number of datapoints to fetch

        Returns:
           res (dict): result in DF4 format
           {
             "head" : { count = 60, start = ..., period = 60 }
             "meta" : [ {kind:"numeric", label:"some_metric"}, {...}, ... ] -- per metric metadata
             "data" : [ [1,1,1,1,...], [2,2,2,2,...] ] -- per metric data
           }
        """
        if isinstance(start, datetime):
            start = start.timestamp()
        if not start % period == 0:
            new_start = math.floor(start / period)
            warnings.warn(
                "start parameter {} is not divisible by period {}. Using {} instead.".format(
                    start, period, new_start))
            start = new_start

        params = {
            "query": query,
            "period": period,
            "start": int(start),
            "end": int(start + count * period),
            "format" : "DF4"
        }
        res = self._api.api_call("GET", "/caql", params=params)

        #
        # Convert histogram JSON values to Circllhist objects.
        #
        # Don't convert histogram output if Circllhist was not found on the system
        if not Circllhist:
            return res

        # In the case of 0 output metrics, res['meta'] itself might be None
        if not res['meta']:
            return res

        assert(len(res['meta']) == len(res['data']))
        width = len(res['meta'])
        for i in range(width):
            if res['meta'][i]['kind'] == "histogram":
                res['data'][i] = [ Circllhist.from_dict(h) for h in res['data'][i] ]

        return res
