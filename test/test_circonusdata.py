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

    def test_caql(self):
        c = self.api.caql("123", datetime(2018,1,1), 60, 10, convert_hists=False)
        self.assertEqual(len(c['data']), 1)
        self.assertEqual(len(c['data'][0]), 10)
        self.assertEqual(c['data'][0][0], 123)

if __name__ == '__main__':
    unittest.main()
