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

try:
    import pandas as pd
except ImportError:
    pd = None


class CirconusData(object):
    "Circonus data fetching class"

    def __init__(self, token):
        self._api = circonusapi.CirconusAPI(token)

    def caql(self, query, start, period, count, convert_hists = True):
        """
        Fetch data using CAQL.

        Args:
           query (str): the CAQL query string
           start (int/dateimte): starttime of the query. Either UNIX timestamp in seconds 
                 or datetime object
           period (int): period of data to fetch
           count (int): number of datapoints to fetch
           convert_hists (boolean, optional): Convert returned histograms to Circllhist objects.
                  Requires Circllhist to be available.

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

        # In the case of 0 output metrics, res['meta']/res['data'] might be None
        if not res['meta']: res['meta'] = []
        if not res['data']: res['data'] = []
        assert(len(res['meta']) == len(res['data']))

        if not convert_hists:
            return res

        #
        # Convert histogram JSON values to Circllhist objects.
        #
        if not Circllhist:
            raise ImportError("Circllhist not available")

        for i in range(len(res['meta'])):
            if res['meta'][i]['kind'] == "histogram":
                res['data'][i] = [ Circllhist.from_dict(h) for h in res['data'][i] ]

        return res

    def caqldf(self, *args, **kwargs):
        """
        Fetch CAQL as pandas DataFrame [1] with:

        - Columns = output metrics
        - Column names = metric labels
        - Row index = Timestamps

        [1] https://pandas.pydata.org/
        """
        if not pd:
            raise ImportError("pandas not available")
        res = self.caql(*args, **kwargs)
        head = res['head']
        meta = res['meta'] or []
        data = res['data'] or []
        return pd.DataFrame(
            data,
            columns = [
                datetime.fromtimestamp(head['start'] + i * head['period'])
                for i in range(head['count'])
            ],
            index = [ m['label'] for m in meta ],
        ).transpose()
