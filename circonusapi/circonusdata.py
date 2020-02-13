"""
Circonus Data Fetching API

This module provides simplified methods for data fetching operations.
To gain access to the full functionality use the circonusapi module.
"""

import math
from datetime import datetime
import warnings
import requests

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

    def __init__(self, token=None, endpoint=None, account=1):
        if token:
            self._mode = "API"
            self._api = circonusapi.CirconusAPI(token)
        elif endpoint:
            self._mode = "IRONdb"
            self._endpoint = endpoint
            self._account = account
        else:
            raise Exception("No token/endpoint given")

    @classmethod
    def from_api(cls, token):
        """
        Connect to the Circonus API with a token

        Args:
           token (str): Circonus API token
        """
        return cls(token = token)

    @classmethod
    def from_irondb(cls, endpoint, account=1):
        """
        Connect to an IRONdb node, instead of a CirconusAPI endpoint

        Args:
           endpoint (str): IRONdb node URL, in the form "<protocol>://<hostname/ip>:<port>",
                           e.g. "http://localhost:8112"
           account (int): account id to use for CAQL requests.

        Notes:
           The current implementation will issue all requests against a single node.
        """
        return cls(endpoint = endpoint, account = account)

    def _caql_request(self, params):
        if self._mode == "API":
            return self._api.api_call("GET", "/caql", params=params)
        elif self._mode == "IRONdb":
            params = dict(params) # copy
            params['account_id'] = self._account
            resp = requests.post(
                self._endpoint + "/extension/lua/caql_v1",
                json=params
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                raise Exception(resp.text)

    def caql(self, query, start, period, count, convert_hists = True, explain=False):
        """
        Fetch data using CAQL.

        Args:
           query (str): the CAQL query string
           start (int/datetime): starttime of the query. Either UNIX timestamp in seconds
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
            "explain" : explain,
            "query": query,
            "period": period,
            "start": int(start),
            "end": int(start + count * period),
            "format" : "DF4"
        }
        res = self._caql_request(params)

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
