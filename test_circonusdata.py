"""
Test for the circonusdata module
"""
#
# circonusdata.py depends on circllhist being available. As this dependency is currently not
# installable via pip we keep these tests in a separate file.
#
import os
from datetime import datetime

import unittest
from unittest import TestCase

from circonusapi import circonusdata, config

class CirconusAPITestCase(TestCase):

    def setUp(self):
        config_file = os.environ.get('CIRCONUS_CONFIG')
        cfg = config.load_config(configfile=config_file, nocache=True)
        account = cfg.get('general', 'default_account')
        token = cfg.get('tokens', account)
        api = circonusdata.CirconusData(token)
        self.api = api

    def test_search(self):
        m = self.api.search("(check_id:160764) (metric:services)")
        self.assertEqual(len(m), 1)
        r = m.fetch(datetime(2018,1,1),60,10)
        self.assertEqual(len(r['time']), 10)

    def test_caql(self):
        c = self.api.caql("search:metric('(check_id:160764) (metric:services)')", datetime(2018,1,1), 60, 10)
        self.assertEqual(len(c['time']), 10)

if __name__ == '__main__':
    unittest.main()
