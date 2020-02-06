"""
Circonus DataSubmission API

This module provides methods to submit data to Circonus via a HTTPTrap check.

Usage Example:

    from circonusapi import circonussubmit

    # Option A: Create a new check to submit data to
    sub = circonussubmit.CirconusSubmit()
    sub.auth("65669d6b-edfe-4ede-bc51-7f3cae6419cf")
    sub.check_create("circ-submit-1")

    # Option B: Use a existing submission URL:
    sub = circonussubmit.CirconusSubmit("<submission url>")

    # Add data to batch
    from datetime import datetime
    sub.add_number(datetime(2020, 1, 1, 0, 0, 0), "test-metric-1", 20)
    sub.add_number(datetime(2020, 1, 1, 0, 1, 0), "test-metric-1", 40)
    sub.add_number(datetime(2020, 1, 1, 0, 2, 0), "test-metric-1", 50)

    # Submit batch of data
    sub.submit()

"""

import sys
import random
import string
import requests
from datetime import datetime

from . import circonusapi
#
# Optional Imports
#

try:
    from circllhist import Circllhist
except ImportError:
    Circllhsit = None


class CirconusSubmit(object):

    def __init__(self, url = None):
        """
        Create CirconusSubmit Object

        Args:
            url (str, optional): URL to submit data to
        """

        # HTTPTrap does not allow us to submit multiple values for the same metrics.  To make-up for
        # this, we keep data in multiple batches, each containing only one value per metric.
        self._batch = []
        self._url = url
        self._api = None

    def _batch_insert(self, name, val):
        i = 0
        while True:
            if i >= len(self._batch):
                self._batch.append({})
                break
            if name in self._batch[i]:
                i += 1
            else:
                break
        assert(not name in self._batch[i])
        self._batch[i][name] = val

    def _batch_reset(self):
        self._batch = []

    def auth(self, token):
        """Authenticate to the API with given token

        Args:
           token (str): API token
        """
        self._api = circonusapi.CirconusAPI(token)

    def check_create(self, name):
        """
        Create new HTTPTrap check with given name, and set submission url accordingly.
        Requires .auth() to be called beforehand.

        Args:
           name (str): Name of check to create
        """
        if self._api is None:
            raise Exception('auth() must be called before check_create()')
        secret = ''.join([ random.choice(string.ascii_lowercase + string.digits) for _ in range(16) ])
        check = self._api.api_call("POST", "/check_bundle", {
            'display_name': name,
            'status': 'active',
            'metrics': [],
            'tags': [],
            'metric_filters': [['allow', '.', 'default']],
            'config': { 'secret': secret, 'asynch_metrics': 'false' },
            'timeout': 10,
            'type': 'httptrap',
            'brokers': ['/broker/35'], # public trap broker
            'period': 60,
            'target': 'localhost'
        })
        sys.stderr.write("Created Check {}".format(check))
        self.check = check
        self._url = check['config']['submission_url']

    def _add(self, ts, name, data):
        if ts == "now":
            ts = datetime.utcnow().timestamp()
        if isinstance(ts, datetime):
            ts = ts.timestamp()
        data['_ts'] = int( ts * 1000 ) # convert to ms
        self._batch_insert(name, data)

    def add_number(self, ts, name, value):
        """
        Add a numeric value to next batch.

        Args:
           ts (number): Timestamp in seconds since epoch.
           name (str): Metric name, including stream tags.
           value (number): value to submit.
        """
        self._add(ts, name, { "_type" : "n", "_value" : value })

    def add_histogram(self, ts, name, hist):
        """
        Add a histogram value to next batch.

        Args:
           ts (number): Timestamp in seconds since epoch, or "now" as a string.
           name (str): Metric name, including stream tags.
           value (CircllHist): value to submit.

        """
        self._add(ts, name, { "_type" : "h", "_value" : hist.to_b64() })

    def submit(self):
        """submit a batch of data"""
        for i, batch in enumerate(self._batch):
            resp = requests.put(self._url, json = batch)
            sys.stderr.write("{}/{} {} - {}\n".format(i+1, len(self._batch), resp, resp.text))
